import cv2
import numpy as np
import time
from typing import Dict, Any, Optional
from soa_kafka_python.utils.producers.producers import BaseProducer
from soa_kafka_python.utils import _log

logger = _log()


class DataProcessor:
    """
    Data processor class with static methods for various data processing operations.
    Designed for extensibility to support multiple data processing methods.
    """
    
    @staticmethod
    def frame_sampling(message_data: Dict[str, Any], 
                      producer: BaseProducer,
                      subsample_rate: int = 15,
                      frame_counter: Optional[Dict[str, int]] = None) -> None:
        """
        Static method for frame sampling processing with enhanced metadata support.
        Implements subsampling logic similar to legacy code.
        
        Args:
            message_data: Dictionary containing enhanced frame data with metadata
            producer: BaseProducer instance for publishing processed frames
            subsample_rate: Take 1 frame every N frames (default: 15)
            frame_counter: Optional dictionary to maintain frame count state
        """
        try:
            # Initialize frame counter if not provided
            if frame_counter is None:
                frame_counter = {'count': 0}
            
            # Extract enhanced frame data
            timestamp = message_data.get('timestamp', time.time())
            frame_bytes = message_data.get('frame')
            
            # Extract video metadata
            video_width = message_data.get('video_width')
            video_height = message_data.get('video_height')
            video_channels = message_data.get('video_channels')
            video_source = message_data.get('video_source')
            frame_id = message_data.get('frame_id')
            source_attributes = message_data.get('source_attributes', {})
            
            if frame_bytes is None:
                logger.warning("No frame data in message")
                return
            
            # Implement subsampling logic
            if frame_counter['count'] % subsample_rate == 0:
                # Prepare enhanced message data for publishing
                processed_message = {
                    'timestamp': float(timestamp),
                    'frame': frame_bytes,
                    # Preserve video metadata
                    'video_width': video_width,
                    'video_height': video_height,
                    'video_channels': video_channels,
                    'video_source': video_source,
                    'frame_id': frame_id,
                    'source_attributes': source_attributes
                }
                
                # Forward the enhanced frame to downstream topic
                producer.publish_message(processed_message, timestamp)
                logger.debug(f"Forwarded frame {frame_counter['count']} (frame_id: {frame_id}) to downstream topic")
            
            frame_counter['count'] += 1
            
            # Log progress periodically with enhanced info
            if frame_counter['count'] % 100 == 0:
                forwarded_count = frame_counter['count'] // subsample_rate
                logger.info(f"Processed {frame_counter['count']} frames from {video_source}, forwarded {forwarded_count} frames")
                
        except Exception as e:
            logger.error(f"Error in frame sampling: {str(e)}")
            raise
    
    @staticmethod
    def create_frame_sampling_processor(producer_id: str, 
                                       subsample_rate: int = 15):
        """
        Factory method to create a frame sampling processor function with enhanced metadata support.
        
        Args:
            producer_id: Producer configuration ID for BaseProducer
            subsample_rate: Take 1 frame every N frames (default: 15)
            
        Returns:
            Callable frame processor function supporting variable arguments
        """
        # Initialize producer and frame counter
        producer = BaseProducer(producer_id)
        frame_counter = {'count': 0}
        
        def processor_function(frame: np.ndarray, timestamp: float, *args) -> None:
            """
            Enhanced processor function that supports variable arguments.
            
            Args:
                frame: Decoded frame as numpy array
                timestamp: Frame timestamp
                *args: Additional arguments (e.g., metadata dictionary)
            """
            try:
                # Re-encode frame to bytes for forwarding
                _, encoded_frame = cv2.imencode('.jpg', frame)
                frame_bytes = encoded_frame.tobytes()
                
                # Create base message data structure
                message_data = {
                    'timestamp': timestamp,
                    'frame': frame_bytes
                }
                
                # If metadata is provided as additional argument, include it
                if args and isinstance(args[0], dict):
                    metadata = args[0]
                    message_data.update({
                        'video_width': metadata.get('video_width'),
                        'video_height': metadata.get('video_height'),
                        'video_channels': metadata.get('video_channels'),
                        'video_source': metadata.get('video_source'),
                        'frame_id': metadata.get('frame_id'),
                        'source_attributes': metadata.get('source_attributes', {})
                    })
                
                DataProcessor.frame_sampling(
                    message_data=message_data,
                    producer=producer,
                    subsample_rate=subsample_rate,
                    frame_counter=frame_counter
                )
            except Exception as e:
                logger.error(f"Error in enhanced processor function: {str(e)}")
                raise
        
        # Attach cleanup method to processor function
        processor_function.cleanup = producer.cleanup
        processor_function.flush = producer.flush
        
        logger.info(f"Enhanced frame sampling processor created with subsample rate: {subsample_rate}")
        return processor_function
    
    # Placeholder for future data processing methods
    @staticmethod
    def image_enhancement(message_data: Dict[str, Any], 
                         producer: BaseProducer,
                         **kwargs) -> None:
        """
        Placeholder for future image enhancement processing.
        
        Args:
            message_data: Dictionary containing image data
            producer: BaseProducer instance for publishing processed data
            **kwargs: Additional parameters for enhancement
        """
        # TODO: Implement image enhancement logic
        pass
    
    @staticmethod
    def data_filtering(message_data: Dict[str, Any], 
                      producer: BaseProducer,
                      filter_criteria: Dict[str, Any]) -> None:
        """
        Placeholder for future data filtering processing.
        
        Args:
            message_data: Dictionary containing data to filter
            producer: BaseProducer instance for publishing filtered data
            filter_criteria: Criteria for data filtering
        """
        # TODO: Implement data filtering logic
        pass


# Example usage
if __name__ == "__main__":
    """
    Example of how to use the frame sampling processor with VideoFrameConsumer.
    This implements subsampling logic from legacy code without detection.
    """
    from soa_data_provider.src.utils.comsumers.consumers import VideoFrameConsumer
    
    try:
        # Create frame sampling processor function (take 1 frame every 15 frames)
        # Note: Replace "camera1_process" with actual producer_id from config.yaml
        frame_processor = DataProcessor.create_frame_sampling_processor(
            producer_id="camera1_process",
            subsample_rate=15
        )
        
        # Create consumer instance
        consumer = VideoFrameConsumer(
            consumer_id="camera1_integration",  # Consumer config ID
            frame_processor=frame_processor     # Our custom processor function
        )
        
        logger.info("Starting frame subsampling from Kafka topic...")
        logger.info("Subsampled frames (1 every 15) will be published to downstream topic")
        
        # Start consuming and processing frames
        consumer.consume_frames()
        
    except KeyboardInterrupt:
        logger.info("Frame processing interrupted by user")
        # Cleanup resources
        if 'frame_processor' in locals() and hasattr(frame_processor, 'cleanup'):
            frame_processor.cleanup()
    except Exception as e:
        logger.error(f"Error in frame processing: {str(e)}")
        # Cleanup resources
        if 'frame_processor' in locals() and hasattr(frame_processor, 'cleanup'):
            frame_processor.cleanup()