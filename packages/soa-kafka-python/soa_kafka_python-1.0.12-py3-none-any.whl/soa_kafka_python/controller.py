import threading
import time
import signal
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from soa_kafka_python.utils.producers.producers import RTSPVideoFrameProducer
from soa_kafka_python.utils.consumers import VideoFrameConsumer
from data_process import DataProcessor
from soa_kafka_python.utils import _log

logger = _log()


class ServiceStatus(Enum):
    """Service status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """Service information data class"""
    name: str
    status: ServiceStatus
    thread: Optional[threading.Thread]
    start_time: Optional[datetime]
    error_message: Optional[str] = None
    restart_count: int = 0


class ServiceObserver(ABC):
    """Service status observer interface"""
    
    @abstractmethod
    def on_status_change(self, service_name: str, old_status: ServiceStatus, new_status: ServiceStatus):
        """Status change callback"""
        pass


class LoggingObserver(ServiceObserver):
    """Logging observer implementation"""
    
    def on_status_change(self, service_name: str, old_status: ServiceStatus, new_status: ServiceStatus):
        logger.info(f"Service '{service_name}' status changed: {old_status.value} -> {new_status.value}")


class Service(ABC):
    """Abstract service base class"""
    
    def __init__(self, name: str):
        self.name = name
        self._stop_event = threading.Event()
        self._observers: List[ServiceObserver] = []
    
    def add_observer(self, observer: ServiceObserver):
        """Add observer"""
        self._observers.append(observer)
    
    def notify_observers(self, old_status: ServiceStatus, new_status: ServiceStatus):
        """Notify observers of status change"""
        for observer in self._observers:
            try:
                observer.on_status_change(self.name, old_status, new_status)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    @abstractmethod
    def run(self):
        """Service run logic"""
        pass
    
    def stop(self):
        """Stop service"""
        self._stop_event.set()
    
    def is_stopped(self) -> bool:
        """Check if service is stopped"""
        return self._stop_event.is_set()


class RTSPProducerService(Service):
    """RTSP producer service"""
    
    def __init__(self, camera_id: str, producer_id: str):
        super().__init__(f"RTSP-{camera_id}")
        self.camera_id = camera_id
        self.producer_id = producer_id
        self.producer = None
    
    def run(self):
        """Run RTSP producer"""
        try:
            logger.info(f"Starting RTSP producer service for camera: {self.camera_id}")
            
            # Create RTSP producer instance
            self.producer = RTSPVideoFrameProducer(
                camera_id=self.camera_id,
                producer_id=self.producer_id
            )
            
            # Run producer
            self.producer.run(max_frames=100)
            
        except Exception as e:
            logger.error(f"RTSP producer service error: {e}")
            raise
        finally:
            if self.producer:
                self.producer.cleanup()


class DataProcessService(Service):
    """Data processing service with enhanced metadata support"""
    
    def __init__(self, consumer_id: str, producer_id: str, subsample_rate: int = 15):
        super().__init__(f"DataProcess-{consumer_id}")
        self.consumer_id = consumer_id
        self.producer_id = producer_id
        self.subsample_rate = subsample_rate
        self.consumer = None
        self.frame_processor = None
    
    def run(self):
        """Run data processing service with enhanced metadata support"""
        try:
            logger.info(f"Starting enhanced data processing service for consumer: {self.consumer_id}")
            
            # Create enhanced frame processor
            self.frame_processor = DataProcessor.create_frame_sampling_processor(
                producer_id=self.producer_id,
                subsample_rate=self.subsample_rate
            )
            
            # Create consumer instance with enhanced frame processor
            self.consumer = VideoFrameConsumer(
                consumer_id=self.consumer_id,
                frame_processor=self.frame_processor
            )
            
            # 使用优化后的 consume_frames 方法
            while not self.is_stopped():
                try:
                    self.consumer.consume_frames(max_frames=100, timeout=1.0)
                except Exception as e:
                    if not self.is_stopped():
                        logger.error(f"Frame consumption error: {e}")
                        time.sleep(1)  # 短暂等待后重试
                    break
            
        except Exception as e:
            logger.error(f"Enhanced data processing service error: {e}")
            raise
        finally:
            if self.consumer and hasattr(self.consumer, 'cleanup'):
                self.consumer.cleanup()
            if self.frame_processor and hasattr(self.frame_processor, 'cleanup'):
                self.frame_processor.cleanup()


class ServiceController:
    """Service controller - using singleton pattern"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.services: Dict[str, ServiceInfo] = {}
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._observers: List[ServiceObserver] = [LoggingObserver()]
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Signal handler"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_all()

    def _update_service_status(self, service_name: str, new_status: ServiceStatus, error_message: str = None):
        """Update service status"""
        if service_name in self.services:
            old_status = self.services[service_name].status
            self.services[service_name].status = new_status
            if error_message:
                self.services[service_name].error_message = error_message

            # Notify observers
            for observer in self._observers:
                try:
                    observer.on_status_change(service_name, old_status, new_status)
                except Exception as e:
                    logger.error(f"Observer notification failed: {e}")

    def add_observer(self, observer: ServiceObserver):
        """Add global observer"""
        self._observers.append(observer)

    def start_service(self, service: Service, auto_restart: bool = True) -> bool:
        """Start service"""
        try:
            service_name = service.name
            
            # Add observers to service
            for observer in self._observers:
                service.add_observer(observer)
            
            # Create service info
            service_info = ServiceInfo(
                name=service_name,
                status=ServiceStatus.STARTING,
                thread=None,
                start_time=datetime.now()
            )
            self.services[service_name] = service_info
            
            # Create and start thread
            def service_wrapper():
                try:
                    self._update_service_status(service_name, ServiceStatus.RUNNING)
                    service.run()
                except Exception as e:
                    error_msg = f"Service {service_name} failed: {str(e)}"
                    logger.error(error_msg)
                    self._update_service_status(service_name, ServiceStatus.ERROR, error_msg)
                    
                    # Auto restart logic
                    if auto_restart and not self._shutdown_event.is_set():
                        self.services[service_name].restart_count += 1
                        if self.services[service_name].restart_count <= 3:
                            logger.info(f"Attempting to restart service {service_name} (attempt {self.services[service_name].restart_count})")
                            time.sleep(5)  # Wait 5 seconds before restart
                            self.start_service(service, auto_restart)
                        else:
                            logger.error(f"Service {service_name} failed too many times, giving up")
                finally:
                    if not self._shutdown_event.is_set():
                        self._update_service_status(service_name, ServiceStatus.STOPPED)
            
            thread = threading.Thread(target=service_wrapper, name=f"Thread-{service_name}")
            thread.daemon = True
            service_info.thread = thread
            thread.start()
            
            logger.info(f"Service {service_name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service {service.name}: {e}")
            self._update_service_status(service.name, ServiceStatus.ERROR, str(e))
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop specified service"""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not found")
            return False
        
        try:
            service_info = self.services[service_name]
            self._update_service_status(service_name, ServiceStatus.STOPPING)
            
            # Stop service thread
            if service_info.thread and service_info.thread.is_alive():
                # Service needs to implement graceful stop mechanism
                service_info.thread.join(timeout=10)
                if service_info.thread.is_alive():
                    logger.warning(f"Service {service_name} did not stop gracefully")
            
            self._update_service_status(service_name, ServiceStatus.STOPPED)
            logger.info(f"Service {service_name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            return False
    
    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service status"""
        return self.services.get(service_name)
    
    def get_all_services_status(self) -> Dict[str, ServiceInfo]:
        """Get all services status"""
        return self.services.copy()
    
    def start_monitoring(self, check_interval: int = 30):
        """Start service monitoring"""
        def monitor_loop():
            while not self._shutdown_event.is_set():
                try:
                    self._check_services_health()
                    time.sleep(check_interval)
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
        
        self._monitor_thread = threading.Thread(target=monitor_loop, name="ServiceMonitor")
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Service monitoring started")
    
    def _check_services_health(self):
        """Check services health status"""
        for service_name, service_info in self.services.items():
            if service_info.thread and not service_info.thread.is_alive():
                if service_info.status == ServiceStatus.RUNNING:
                    logger.warning(f"Service {service_name} thread died unexpectedly")
                    self._update_service_status(service_name, ServiceStatus.ERROR, "Thread died unexpectedly")
    
    def shutdown_all(self):
        """Shutdown all services"""
        logger.info("Shutting down all services...")
        self._shutdown_event.set()
        
        # Stop all services
        for service_name in list(self.services.keys()):
            self.stop_service(service_name)
        
        # Stop monitoring thread
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        
        logger.info("All services shut down")


def main():
    """Main function - demonstrates how to use service controller"""
    try:
        # Create service controller instance
        controller = ServiceController()
        
        # Create service instances
        rtsp_service = RTSPProducerService(
            camera_id="camera1",
            producer_id="camera1_integration"
        )
        
        data_process_service = DataProcessService(
            consumer_id="camera1_integration",
            producer_id="camera1_process",
            subsample_rate=5
        )
        
        # Start services
        logger.info("Starting services...")
        controller.start_service(rtsp_service)
        time.sleep(2)  # Wait for RTSP service to start
        controller.start_service(data_process_service)
        
        # Start monitoring
        controller.start_monitoring(check_interval=30)
        
        # Periodically print service status
        while True:
            time.sleep(60)
            services_status = controller.get_all_services_status()
            logger.info("=== Services Status ===")
            for name, info in services_status.items():
                logger.info(f"{name}: {info.status.value} (restarts: {info.restart_count})")
                if info.error_message:
                    logger.info(f"  Error: {info.error_message}")
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        controller.shutdown_all()
        sys.exit(0)


if __name__ == "__main__":
    main()
