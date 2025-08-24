import sys
from pathlib import Path
import threading
import time
import uuid
import json
from typing import Dict, Any, Optional, Callable, List
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import re

# Add parent directory to Python path
current_file = Path(__file__)
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from utils.common_utils import _log, config_loader
from utils.producers.producers import BaseProducer
from utils.consumers.consumers import BaseKafkaConsumer
from utils.db_conn_utils import get_database_connector

import re

logger = _log()
config_dict = config_loader()


class QueryRequestConsumer(BaseKafkaConsumer):
    
    def __init__(self, consumer_id: str, query_processor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        super().__init__(consumer_id)
        self.query_processor = query_processor
        
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        try:
            logger.info(f"Processing query request: {data.get('query_id', 'unknown')}")
            self.query_processor(data)
        except Exception as e:
            logger.error(f"Error processing query request: {str(e)}")


class QueryResponseConsumer(BaseKafkaConsumer):
    
    def __init__(self, consumer_id: str, response_handler: Callable[[Dict[str, Any]], None]):
        super().__init__(consumer_id)
        self.response_handler = response_handler
        
    def _process_message_data(self, data: Dict[str, Any]) -> None:
        try:
            logger.info(f"Processing query response: {data.get('query_id', 'unknown')}")
            self.response_handler(data)
        except Exception as e:
            logger.error(f"Error processing query response: {str(e)}")


class SOADataQueryManager:
    
    def __init__(self, db_connection_id, db_connection_config):
        
        self.db_connection_id = db_connection_id
        self.db_connection_config = db_connection_config
        self.db_connector = None
        
        self.query_request_producer = None
        self.query_response_producer = None
        self.query_request_consumer = None
        self.query_response_consumer = None
        
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        self.consumer_threads = []
        
        self.query_results = {}
        self.result_queues = {}
        self.query_lock = threading.Lock()

        self.initialize()
        self.start_consumers()
        
        logger.info("SOADataQueryManager initialized")
    
    def initialize(self):
        try:
            self.db_connector = get_database_connector(self.db_connection_id, self.db_connection_config)
            logger.info(f"Database connector initialized for: {self.db_connection_id}")
            
            self.query_request_producer = BaseProducer("query_request")
            self.query_response_producer = BaseProducer("query_response")
            logger.info("Producers initialized")
            
            self.query_request_consumer = QueryRequestConsumer(
                "query_request", 
                self._handle_query_request
            )

            self.query_response_consumer = QueryResponseConsumer(
                "query_response", 
                self._handle_query_response
            )
            logger.info("Consumers initialized")
            
        except Exception as e:
            logger.error(f"Error initializing SOADataQueryManager: {str(e)}")
            raise
    
    def start_consumers(self):
        if self.running:
            logger.warning("Consumers are already running")
            return
            
        self.running = True

        logger.warning("多线程代码启动")
        
        request_thread = threading.Thread(
            target=self._run_consumer,
            args=(self.query_request_consumer, "query_request"),
            daemon=True
        )
        request_thread.start()
        self.consumer_threads.append(request_thread)
        
        response_thread = threading.Thread(
            target=self._run_consumer,
            args=(self.query_response_consumer, "query_response"),
            daemon=True
        )
        response_thread.start()
        self.consumer_threads.append(response_thread)
        
        logger.info("All consumers started")
    
    def _run_consumer(self, consumer: BaseKafkaConsumer, consumer_name: str):
        try:
            logger.info(f"Starting {consumer_name} consumer")
            while self.running:
                try:
                    msg = consumer._poll_and_handle_message(timeout=1.0)
                    logger.info(msg)
                    if msg is None:
                        continue
                    
                    data = consumer._deserialize_message(msg)
                    consumer._process_message_data(data)
                    
                except Exception as e:
                    logger.error(f"Error in {consumer_name} consumer: {str(e)}")
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Fatal error in {consumer_name} consumer: {str(e)}")
        finally:
            logger.info(f"{consumer_name} consumer stopped")
    
    def _is_select_query(self, sql_query: str) -> bool:
        
        cleaned_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
        cleaned_query = re.sub(r'--.*?\n', '\n', cleaned_query)
        cleaned_query = cleaned_query.strip()
        
        select_pattern = r'^\s*(SELECT|WITH)\s+'
        return bool(re.match(select_pattern, cleaned_query, re.IGNORECASE))
    
    def _handle_query_request(self, request_data: Dict[str, Any]):
        try:
            app_id = request_data.get('app_id', 'unknown')
            query_id = request_data.get('query_id')
            query_statement = request_data.get('query_statement')  # 使用schema中的字段名
            query_type = request_data.get('query_type')
            parameters = request_data.get('parameters', {})
            
            if not query_id or not query_statement:
                logger.error("Invalid query request: missing query_id or query_statement")
                return
            
            logger.info(f"Executing query {query_id} from app {app_id}: {query_statement}")
            
            start_time = time.time()
            
            try:
                is_select = self._is_select_query(query_statement)
                
                if is_select:
                    results = self.db_connector.execute_query(query_statement)
                    result_data = json.dumps(results, ensure_ascii=False) if results else None
                    row_count = len(results) if results else 0
                    status = "success"
                    error_message = None
                else:
                    affected_rows = self.db_connector.execute_non_query(query_statement)
                    result_data = json.dumps({"affected_rows": affected_rows}, ensure_ascii=False)
                    row_count = affected_rows
                    status = "success"
                    error_message = None
                    
            except Exception as e:
                logger.error(f"Database query failed for {query_id}: {str(e)}")
                result_data = None
                row_count = None
                status = "error"
                error_message = str(e)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            response_data = {
                'app_id': app_id,
                'query_id': query_id,
                'timestamp': time.time(),
                'status': status,
                'result_data': result_data,
                'error_message': error_message,
                'execution_time_ms': execution_time_ms,
                'row_count': row_count,
                'metadata': {
                    'query_type': query_type or ('select' if self._is_select_query(query_statement) else 'non_query'),
                    'original_query': query_statement[:100] + '...' if len(query_statement) > 100 else query_statement
                } if query_type or query_statement else None
            }
            
            self.query_response_producer.publish_message(response_data)
            logger.info(f"Query response published for {query_id} with status: {status}")
            
        except Exception as e:
            logger.error(f"Error handling query request: {str(e)}")
    
    def submit_query(self, sql_query: str, query_id: Optional[str] = None, app_id: str = "soa_data_utils", query_type: Optional[str] = None) -> str:
        if not self.query_request_producer:
            raise RuntimeError("SOADataQueryManager not initialized. Call initialize() first.")
        
        if query_id is None:
            query_id = str(uuid.uuid4())
        
        request_data = {
            'app_id': app_id,
            'query_id': query_id,
            'timestamp': time.time(),
            'query_statement': sql_query,  # 使用schema中的字段名
            'query_type': query_type,
            'parameters': None  # 可以根据需要扩展参数支持
        }
        
        self.query_request_producer.publish_message(request_data)
        logger.info(f"Query submitted with ID: {query_id} from app: {app_id}")
        
        return query_id
    
    def _handle_query_response(self, response_data: Dict[str, Any]):
        try:
            query_id = response_data.get('query_id')
            if not query_id:
                logger.error("Invalid query response: missing query_id")
                return
            
            with self.query_lock:
                self.query_results[query_id] = response_data
                
                if query_id in self.result_queues:
                    self.result_queues[query_id].put(response_data)
            
            logger.info(f"Query response processed for {query_id}")
            
        except Exception as e:
            logger.error(f"Error handling query response: {str(e)}")
    
    def get_query_result(self, query_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        with self.query_lock:
            if query_id in self.query_results:
                return self.query_results[query_id]
            
            if query_id not in self.result_queues:
                self.result_queues[query_id] = Queue()
        
        try:
            result = self.result_queues[query_id].get(timeout=timeout)
            return result
        except Empty:
            logger.warning(f"Query {query_id} timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error getting query result for {query_id}: {str(e)}")
            return None
        finally:
            with self.query_lock:
                if query_id in self.result_queues:
                    del self.result_queues[query_id]
    
    def execute_query_sync(self, sql_query: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        query_id = self.submit_query(sql_query)
        return self.get_query_result(query_id, timeout)
    
    def stop_consumers(self):
        if not self.running:
            logger.warning("Consumers are not running")
            return
        
        logger.info("Stopping consumers...")
        self.running = False
        
        for thread in self.consumer_threads:
            thread.join(timeout=5.0)
        
        self.consumer_threads.clear()
        logger.info("All consumers stopped")
    
    def cleanup(self):
        try:
            self.stop_consumers()
            
            if self.query_request_producer:
                self.query_request_producer.cleanup()
            if self.query_response_producer:
                self.query_response_producer.cleanup()
            
            if self.query_request_consumer:
                self.query_request_consumer.cleanup()
            if self.query_response_consumer:
                self.query_response_consumer.cleanup()
            
            self.executor.shutdown(wait=True)
            
            logger.info("SOADataQueryManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def __del__(self):
        self.cleanup()
    

if __name__ == "__main__":
    """
    """
    # Test three connector
    query_manager = SOADataQueryManager(db_connection_id="nonv_postgres_db", db_connection_config=None)
    #query_manager = SOADataQueryManager(db_connection_id="nonv_mssql_db", db_connection_config=None)
    #query_manager = SOADataQueryManager(db_connection_id="nonv_aws_db", db_connection_config=None)

    query_pg_sql = "SELECT version()"
    query_ms_sql = "SELECT @@VERSION"
    query_aws_sql = "select * from \"prod-timestream-otdhl\".\"CN_TI_TP2_FL71\" where quality = 'GOOD' and time > '2025-08-23 00:00:00' and physicalmodel = 'CN_TI_TP2_FL71_FM_Infeed_Plate_AlarmEH080'"
 
    result = query_manager.execute_query_sync(
        query_pg_sql,
        timeout=10.0
    )

    if result:
        if result['status'] == 'success':
            print(f"Query results: {result}")
        else:
            print(f"Query failed: {result}")
    else:
        print("Query timed out")

    # query_manager.cleanup()

    # # # 或者异步方式
    # query_id = query_manager.submit_query("SELECT COUNT(*) FROM public.pod_information;")
    # print(f"Submitted query with ID: {query_id}")
    #
    # # 稍后获取结果
    # time.sleep(2)
    # result = query_manager.get_query_result(query_id)
    # if result:
    #     print(f"Async query result: {result}")
