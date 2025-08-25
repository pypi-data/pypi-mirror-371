import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any
import uuid
from datetime import datetime

# Add parent directory to Python path
current_file = Path(__file__)
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from soa_kafka_python.utils.producers.producers import NotificationProducer
from soa_kafka_python.utils.consumers.consumers import NotificationConsumer
from soa_kafka_python.utils.common_utils import _log

logger = _log()

class NotificationDemo:
    """
    邮件通知系统演示类，展示邮件通知的发布和处理流程。
    """
    
    def __init__(self):
        """初始化演示类。"""
        self.producer = None
        self.consumer = None
        self.consumer_thread = None
        self.stop_consumer = False
        
    def setup_producer(self):
        """设置通知生产者。"""
        try:
            logger.info("正在初始化通知生产者...")
            self.producer = NotificationProducer("notification")
            logger.info("通知生产者初始化成功")
        except Exception as e:
            logger.error(f"通知生产者初始化失败: {e}")
            raise
    
    def setup_consumer(self):
        """设置通知消费者。"""
        try:
            logger.info("正在初始化通知消费者...")
            self.consumer = NotificationConsumer(
                "notification",
                notification_processor=self.custom_notification_processor
            )
            logger.info("通知消费者初始化成功")
        except Exception as e:
            logger.error(f"通知消费者初始化失败: {e}")
            raise
    
    def custom_notification_processor(self, data: Dict[str, Any]):
        """自定义通知处理器，用于演示邮件通知。"""
        notification_type = data.get('notification_type')
        app_id = data.get('app_id')
        notification_id = data.get('notification_id')
        title = data.get('title')
        timestamp = data.get('timestamp')
        
        logger.info(f"\n=== 收到通知 ===")
        logger.info(f"应用ID: {app_id}")
        logger.info(f"通知ID: {notification_id}")
        logger.info(f"通知类型: {notification_type}")
        logger.info(f"标题: {title}")
        logger.info(f"时间戳: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if notification_type == 'EMAIL':
            self._demo_process_email(data)
        else:
            logger.info(f"此演示仅处理邮件通知，跳过类型: {notification_type}")
    
    def _demo_process_email(self, data: Dict[str, Any]):
        """演示邮件通知处理。"""
        email_details = data.get('email_details', {})
        recipients = data.get('recipients', [])
        message = data.get('message')
        priority = data.get('priority', 'MEDIUM')
        sender = data.get('sender')
        metadata = data.get('metadata', {})
        
        logger.info(f"邮件主题: {email_details.get('subject')}")
        logger.info(f"收件人: {', '.join(recipients)}")
        logger.info(f"邮件内容: {message}")
        logger.info(f"发送者: {sender}")
        logger.info(f"优先级: {priority}")
        
        # 模拟发送邮件过程
        print("\n📧 模拟发送邮件:")
        print(f"   发送者: {sender or 'system@company.com'}")
        print(f"   发送至: {', '.join(recipients)}")
        print(f"   主题: {email_details.get('subject')}")
        print(f"   内容: {message}")
        print(f"   优先级: {priority}")
        
        if email_details.get('html_content'):
            print(f"   HTML内容: {email_details.get('html_content')[:50]}...")
        
        if email_details.get('cc_recipients'):
            print(f"   抄送: {', '.join(email_details.get('cc_recipients'))}")
        
        if email_details.get('bcc_recipients'):
            print(f"   密送: {', '.join(email_details.get('bcc_recipients'))}")
        
        if email_details.get('attachments'):
            print(f"   附件: {', '.join(email_details.get('attachments'))}")
        
        if metadata:
            print(f"   元数据: {metadata}")
        
        print("   ✅ 邮件发送成功（模拟）")
    
    def start_consumer_thread(self):
        """在后台线程中启动消费者。"""
        def consumer_worker():
            logger.info("消费者线程启动")
            try:
                while not self.stop_consumer:
                    self.consumer.consume_notifications(max_notifications=1, timeout=1.0)
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"消费者线程异常: {e}")
            logger.info("消费者线程结束")
        
        self.consumer_thread = threading.Thread(target=consumer_worker, daemon=True)
        self.consumer_thread.start()
        logger.info("消费者后台线程已启动")
    
    def publish_email_notification_demo(self):
        """发布邮件通知演示。"""
        notification_id = str(uuid.uuid4())
        
        logger.info(f"\n=== 发布邮件通知演示 ===")
        logger.info(f"通知ID: {notification_id}")
        
        try:
            self.producer.publish_email_notification(
                app_id="demo_app",
                notification_id=notification_id,
                title="系统告警通知",
                message="检测到生产线异常，请及时处理。",
                recipients=["operator1@company.com", "supervisor@company.com"],
                subject="【紧急】生产线异常告警",
                html_content="<h2>系统告警</h2><p>检测到生产线异常，请及时处理。</p><p>时间: {}</p>".format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
                cc_recipients=["manager@company.com"],
                bcc_recipients=["admin@company.com"],
                attachments=["/path/to/error_log.txt", "/path/to/system_status.pdf"],
                sender="system@company.com",
                priority="HIGH",
                metadata={
                    "source": "production_line_monitor",
                    "alert_type": "equipment_failure",
                    "location": "workshop_a",
                    "severity": "critical"
                },
                retry_count=3,
                expiry_timestamp=time.time() + 3600  # 1小时后过期
            )
            
            logger.info("✅ 邮件通知发布成功")
            
        except Exception as e:
            logger.error(f"❌ 邮件通知发布失败: {e}")
    
    def run_demo(self):
        """运行邮件通知演示。"""
        try:
            print("\n" + "="*60)
            print("           邮件通知系统演示程序")
            print("           (基于soa.notification.json.broadcast.v1.dev)")
            print("="*60)
            
            # 1. 初始化组件
            print("\n🔧 步骤1: 初始化通知系统组件")
            self.setup_producer()
            self.setup_consumer()
            
            # 2. 启动消费者
            print("\n🚀 步骤2: 启动通知消费者")
            self.start_consumer_thread()
            
            # 等待消费者启动
            time.sleep(2)
            
            # 3. 发布邮件通知
            print("\n📧 步骤3: 发布邮件通知")
            self.publish_email_notification_demo()
            
            # 等待处理
            time.sleep(5)
            
            # 4. 显示统计信息
            print("\n📊 步骤4: 显示处理统计")
            stats = self.consumer.get_notification_stats()
            print(f"通知处理统计: {stats}")
            
        except Exception as e:
            logger.error(f"演示运行失败: {e}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源。"""
        print("\n🧹 清理资源...")
        
        # 停止消费者
        self.stop_consumer = True
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5)
        
        # 清理生产者
        if self.producer:
            self.producer.flush()
            self.producer.cleanup()
        
        # 清理消费者
        if self.consumer:
            self.consumer.cleanup()
        
        logger.info("资源清理完成")


def main():
    """主函数。"""
    demo = NotificationDemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        logger.error(f"演示失败: {e}", exc_info=True)
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()