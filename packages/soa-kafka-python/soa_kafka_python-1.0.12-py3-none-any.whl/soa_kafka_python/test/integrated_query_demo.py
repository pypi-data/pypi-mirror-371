import sys
import time
import threading
import uuid
import json
from pathlib import Path
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

# Add parent directory to Python path
current_file = Path(__file__)
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from soa_kafka_python.utils.producers.producers import QueryRequestProducer
from soa_kafka_python.utils.consumers.consumers import QueryRequestConsumer, QueryResponseConsumer
from soa_kafka_python.utils.db_conn_utils import get_database_connector

logging.basicConfig(
        level=logging.WARN,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class IntegratedQueryDemo:
    """
    集成查询演示类，在一个脚本中实现完整的查询流程：
    1. 发布查询请求
    2. 接受查询请求
    3. 处理查询（执行数据库查询）
    4. 返回查询结果
    查询完成后自动关闭所有consumer
    """
    
    def __init__(self, app_id: str = "integrated_demo", db_connection_id: str = "aws_db_eh080"):
        """初始化集成查询演示类。"""
        self.app_id = app_id
        self.db_connection_id = db_connection_id
        
        # 组件
        self.request_producer = None
        self.request_consumer = None
        self.response_consumer = None
        
        # 线程管理
        self.request_consumer_thread = None
        self.response_consumer_thread = None
        self.stop_consumers = False
        
        # 查询结果管理
        self.query_results = {}
        self.query_futures = {}
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # 数据库连接
        self.db_connector = None
        
    def setup_components(self):
        """设置所有组件。"""
        try:
            print("正在初始化所有组件...")
            
            # 1. 初始化数据库连接
            print(f"初始化数据库连接: {self.db_connection_id}")
            self.db_connector = get_database_connector(self.db_connection_id)
            
            # 测试数据库连接
            version_result = self.db_connector.execute_query("SELECT version()")
            print(f"数据库连接成功: {version_result[0] if version_result else 'Unknown'}")
            
            # 2. 初始化查询请求生产者
            print("初始化查询请求生产者...")
            self.request_producer = QueryRequestProducer("query_request")
            
            # 3. 初始化查询请求消费者
            print("初始化查询请求消费者...")
            self.request_consumer = QueryRequestConsumer(
                consumer_id="query_request",
                db_connection_id=self.db_connection_id,
                response_producer_id="query_response"
            )
            
            # 4. 初始化查询响应消费者
            print("初始化查询响应消费者...")
            self.response_consumer = QueryResponseConsumer(
                "query_response",
                response_processor=self.process_query_response
            )
            
            print("所有组件初始化完成")
            
        except Exception as e:
            logging.error(f"组件初始化失败: {e}")
            raise
    
    def start_consumers(self):
        """启动所有消费者线程。"""
        print("启动消费者线程...")
        
        # 启动查询请求消费者线程
        def request_consumer_worker():
            print("查询请求消费者线程启动")
            try:
                while not self.stop_consumers:
                    self.request_consumer.consume_requests(max_requests=1, timeout=1.0)
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"查询请求消费者线程异常: {e}")
            print("查询请求消费者线程结束")
        
        # 启动查询响应消费者线程
        def response_consumer_worker():
            print("查询响应消费者线程启动")
            try:
                while not self.stop_consumers:
                    self.response_consumer.consume_responses(max_responses=1, timeout=1.0)
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"查询响应消费者线程异常: {e}")
            print("查询响应消费者线程结束")
        
        self.request_consumer_thread = threading.Thread(target=request_consumer_worker, daemon=True)
        self.response_consumer_thread = threading.Thread(target=response_consumer_worker, daemon=True)
        
        self.request_consumer_thread.start()
        self.response_consumer_thread.start()
        
        print("所有消费者线程已启动")
        
        # 等待消费者启动
        time.sleep(2)
    
    def process_query_response(self, data: Dict[str, Any]):
        """处理查询响应。"""
        try:
            query_id = data.get('query_id')
            app_id = data.get('app_id')
            
            # 只处理本应用的响应
            if app_id != self.app_id:
                return
            
            print(f"收到查询响应: query_id={query_id}, status={data.get('status')}")
            
            # 存储查询结果
            self.query_results[query_id] = data
            
            # 如果有等待的 Future，设置结果
            if query_id in self.query_futures:
                future = self.query_futures[query_id]
                if not future.done():
                    future.set_result(data)
                    
        except Exception as e:
            logging.error(f"处理查询响应时出错: {e}")
    
    def submit_query(self, sql: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """提交查询并等待结果。"""
        query_id = str(uuid.uuid4())
        
        try:
            print(f"提交查询: query_id={query_id}")
            print(f"SQL: {sql}")
            
            # 创建 Future 用于等待结果
            future = Future()
            self.query_futures[query_id] = future
            
            # 发布查询请求
            self.request_producer.publish_query_request(
                app_id=self.app_id,
                query_id=query_id,
                query_statement=sql,
                query_type="sql"
            )
            
            # 等待结果
            try:
                result = future.result(timeout=timeout_seconds)
                print(f"查询完成: query_id={query_id}, status={result.get('status')}")
                return result
            except Exception as e:
                logging.error(f"查询超时或失败: query_id={query_id}, error={e}")
                return {
                    'query_id': query_id,
                    'status': 'timeout',
                    'error_message': f'查询超时: {str(e)}',
                    'result_data': None
                }
                
        except Exception as e:
            logging.error(f"提交查询失败: {e}")
            return {
                'query_id': query_id,
                'status': 'error',
                'error_message': f'提交查询失败: {str(e)}',
                'result_data': None
            }
        finally:
            # 清理 Future
            if query_id in self.query_futures:
                del self.query_futures[query_id]
    
    def display_query_result(self, result: Dict[str, Any]):
        """显示查询结果。"""
        print("\n" + "="*60)
        print("                查询结果")
        print("="*60)
        
        print(f"查询ID: {result.get('query_id')}")
        print(f"应用ID: {result.get('app_id', 'N/A')}")
        print(f"状态: {result.get('status')}")
        
        if result.get('timestamp'):
            timestamp = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"时间戳: {timestamp}")
        
        if result.get('status') == 'success':
            print(f"执行时间: {result.get('execution_time_ms', 0)}ms")
            print(f"返回行数: {result.get('row_count', 0)}")
            
            if result.get('result_data'):
                try:
                    data = json.loads(result['result_data'])
                    print("\n查询结果数据:")
                    
                    if isinstance(data, list) and len(data) > 0:
                        # 显示表头
                        if isinstance(data[0], dict):
                            headers = list(data[0].keys())
                            print(f"  {' | '.join(headers)}")
                            print(f"  {'-' * (len(' | '.join(headers)))}")
                            
                            # 显示数据行（最多显示10行）
                            for i, row in enumerate(data[:10]):
                                values = [str(row.get(h, ''))[:20] for h in headers]  # 限制列宽
                                print(f"  {' | '.join(values)}")
                            
                            if len(data) > 10:
                                print(f"  ... 还有 {len(data) - 10} 行数据")
                        else:
                            # 简单列表数据
                            for i, item in enumerate(data[:10]):
                                print(f"  {i+1}: {item}")
                            if len(data) > 10:
                                print(f"  ... 还有 {len(data) - 10} 项数据")
                    else:
                        print(f"  {data}")
                        
                except json.JSONDecodeError:
                    print(f"  原始数据: {result['result_data'][:500]}...")
        else:
            print(f"错误信息: {result.get('error_message', '未知错误')}")
        
        print("="*60)
    
    def run_demo_queries(self, queries: List[Dict[str, str]]):
        """运行演示查询列表。"""
        print("\n" + "="*80)
        print("                集成查询演示程序")
        print("        (发布->接受->处理->返回 完整流程)")
        print("="*80)
        
        for i, query_info in enumerate(queries, 1):
            print(f"\n🔍 查询 {i}: {query_info['name']}")
            print(f"描述: {query_info['description']}")
            print(f"SQL: {query_info['sql']}")
            
            # 提交查询并获取结果
            result = self.submit_query(query_info['sql'])
            
            # 显示结果
            self.display_query_result(result)
            
            # 等待一下再执行下一个查询
            if i < len(queries):
                time.sleep(1)
    
    def run_single_query(self, sql: str, description: str = ""):
        """运行单个查询。"""
        print("\n" + "="*80)
        print("                集成查询演示程序")
        print("        (发布->接受->处理->返回 完整流程)")
        print("="*80)
        
        print(f"\n🔍 执行查询")
        if description:
            print(f"描述: {description}")
        print(f"SQL: {sql}")
        
        # 提交查询并获取结果
        result = self.submit_query(sql)
        
        # 显示结果
        self.display_query_result(result)
        
        return result
    
    def cleanup(self):
        """清理所有资源。"""
        print("\n🧹 清理资源...")
        
        # 停止所有消费者
        self.stop_consumers = True
        
        # 等待消费者线程结束
        if self.request_consumer_thread and self.request_consumer_thread.is_alive():
            self.request_consumer_thread.join(timeout=5)
        
        if self.response_consumer_thread and self.response_consumer_thread.is_alive():
            self.response_consumer_thread.join(timeout=5)
        
        # 清理生产者
        if self.request_producer:
            self.request_producer.flush()
            self.request_producer.cleanup()
        
        # 清理消费者
        if self.request_consumer:
            self.request_consumer.cleanup()
        
        if self.response_consumer:
            self.response_consumer.cleanup()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 清理数据库连接
        if self.db_connector:
            self.db_connector.cleanup()
        
        print("所有资源清理完成")
        print("✅ 所有consumer已关闭，资源清理完成")
    
    def run_demo(self, queries: Optional[List[Dict[str, str]]] = None):
        """运行完整演示。"""
        try:
            # 1. 初始化所有组件
            print("\n🔧 步骤1: 初始化所有组件")
            self.setup_components()
            
            # 2. 启动消费者
            print("\n🚀 步骤2: 启动所有消费者")
            self.start_consumers()
            
            # 3. 运行查询
            print("\n📊 步骤3: 执行查询")
            

            default_queries = [
                {
                    "name": "Pod 信息统计",
                    "sql": "SELECT * FROM public.pod_information;",
                    "description": "统计 pod_information 表的总行数"
                },
                {
                    "name": "Pod 信息统计",
                    "sql": "SELECT count(*) FROM public.pod_information;",
                    "description": "统计 pod_information 表的总行数"
                }
            ]
            self.run_demo_queries(default_queries)
            
            print("\n✅ 查询演示完成！")
            print("\n📋 演示总结:")
            print("   - ✅ 发布查询请求到 adhoc.query.request.v1.dev")
            print("   - ✅ 接受并处理查询请求")
            print("   - ✅ 执行数据库查询")
            print("   - ✅ 返回查询结果到 adhoc.query.response.v1.dev")
            print("   - ✅ 接收并显示查询结果")
            
        except Exception as e:
            logging.error(f"演示运行失败: {e}")
            raise
        finally:
            # 4. 清理所有资源
            print("\n🧹 步骤4: 清理所有资源")
            self.cleanup()


def main():
    
    demo = IntegratedQueryDemo(
        app_id="integrated_demo",
        db_connection_id="aws_db_eh080"
    )

    demo.run_demo()


if __name__ == "__main__":
    main()