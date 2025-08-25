import cv2
import numpy as np
import os
from datetime import datetime
from typing import Optional

from soa_kafka_python.utils.consumers.consumers import VideoFrameConsumer
from soa_kafka_python.utils.common_utils import _log

logger = _log()


class FrameToImageSaver:
    """
    Frame saver class that uses VideoFrameConsumer to save frames as JPG images.
    """
    
    def __init__(self, output_dir: str = "output_frames", max_frames: Optional[int] = None):
        """
        Initialize FrameToImageSaver.
        
        Args:
            output_dir: Directory to save images (relative to project root)
            max_frames: Maximum number of frames to save, None means unlimited
        """
        self.output_dir = output_dir
        self.max_frames = max_frames
        self.saved_count = 0
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory: {os.path.abspath(self.output_dir)}")
    
    def frame_processor(self, frame: np.ndarray, timestamp: float, *args) -> None:
        """
        Process and save frame as JPG image with enhanced metadata logging.
        
        Args:
            frame: Decoded frame as numpy array
            timestamp: Frame timestamp
            *args: Additional arguments (e.g., metadata dictionary)
        """
        try:
            # Check if we've reached the maximum number of frames
            if self.max_frames is not None and self.saved_count >= self.max_frames:
                logger.info(f"Reached maximum frames limit: {self.max_frames}")
                return
            
            # Extract metadata if provided
            metadata = {}
            if args and isinstance(args[0], dict):
                metadata = args[0]
            
            # Generate filename with timestamp
            dt = datetime.fromtimestamp(timestamp)
            filename = f"frame_{dt.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            # Log enhanced metadata information with clear formatting
            logger.info("=" * 80)
            logger.info(f"📸 PROCESSING FRAME #{self.saved_count + 1}")
            logger.info("=" * 80)
            
            # Basic frame information
            logger.info(f"🕒 Timestamp: {timestamp} ({dt.strftime('%Y-%m-%d %H:%M:%S.%f')})")
            logger.info(f"📁 Filename: {filename}")
            logger.info(f"📐 Frame Shape: {frame.shape} (H×W×C: {frame.shape[0]}×{frame.shape[1]}×{frame.shape[2] if len(frame.shape) > 2 else 1})")
            
            # Enhanced metadata from new schema
            if metadata:
                logger.info("-" * 40 + " VIDEO METADATA " + "-" * 40)
                
                # Video dimensions
                video_width = metadata.get('video_width')
                video_height = metadata.get('video_height')
                video_channels = metadata.get('video_channels')
                if video_width and video_height:
                    logger.info(f"📺 Video Resolution: {video_width}×{video_height}×{video_channels}")
                
                # Video source information
                video_source = metadata.get('video_source')
                if video_source:
                    logger.info(f"🎥 Video Source: {video_source}")
                
                # Frame ID
                frame_id = metadata.get('frame_id')
                if frame_id is not None:
                    logger.info(f"🆔 Frame ID: {frame_id}")
                
                # Source attributes
                source_attributes = metadata.get('source_attributes', {})
                if source_attributes:
                    logger.info("-" * 35 + " SOURCE ATTRIBUTES " + "-" * 35)
                    source_type = source_attributes.get('source_type')
                    fps = source_attributes.get('fps')
                    quality = source_attributes.get('quality')
                    encoding = source_attributes.get('encoding')
                    
                    if source_type:
                        logger.info(f"🔧 Source Type: {source_type.upper()}")
                    if fps:
                        logger.info(f"🎬 FPS: {fps}")
                    if quality:
                        logger.info(f"🎯 Quality: {quality}%")
                    if encoding:
                        logger.info(f"📦 Encoding: {encoding.upper()}")
            else:
                logger.info("-" * 40 + " NO METADATA " + "-" * 40)
                logger.info("⚠️  No enhanced metadata available (using legacy schema)")
            
            # Save frame as JPG with original quality (no compression)
            success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            
            if success:
                self.saved_count += 1
                file_size = os.path.getsize(filepath)
                logger.info("-" * 40 + " SAVE RESULT " + "-" * 40)
                logger.info(f"✅ Successfully saved frame to: {filename}")
                logger.info(f"💾 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                logger.info(f"📊 Total frames saved: {self.saved_count}")
            else:
                logger.error("-" * 40 + " SAVE ERROR " + "-" * 40)
                logger.error(f"❌ Failed to save frame: {filename}")
            
            logger.info("=" * 80)
            logger.info("")  # Empty line for better readability
                
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"💥 ERROR PROCESSING FRAME #{self.saved_count + 1}")
            logger.error("=" * 80)
            logger.error(f"❌ Error details: {str(e)}")
            logger.error(f"🕒 Timestamp: {timestamp}")
            logger.error(f"📐 Frame shape: {frame.shape if frame is not None else 'None'}")
            logger.error("=" * 80)
            logger.error("")  # Empty line for better readability
    
    def start_saving(self, consumer_id: str = "camera1_process_saver"):
        """
        Start consuming and saving frames.
        
        Args:
            consumer_id: Consumer configuration ID
        """
        try:
            # Create VideoFrameConsumer with our frame processor
            consumer = VideoFrameConsumer(
                consumer_id=consumer_id,
                frame_processor=self.frame_processor
            )
            
            logger.info(f"Starting to consume frames and save to {self.output_dir}")
            logger.info(f"Subscribing to topic via consumer config: {consumer_id}")
            
            if self.max_frames:
                logger.info(f"Will save maximum {self.max_frames} frames")
            else:
                logger.info("Will save frames indefinitely (Ctrl+C to stop)")
            
            # Start consuming frames
            consumer.consume_frames(max_frames=self.max_frames)
            
        except KeyboardInterrupt:
            logger.info("Frame saving interrupted by user")
        except Exception as e:
            logger.error(f"Error in frame saving: {str(e)}")
        finally:
            logger.info(f"Total frames saved: {self.saved_count}")


def main():
    """
    Main function to run the frame saver.
    """
    # Configuration
    OUTPUT_DIR = "output_frames"  # Output directory
    MAX_FRAMES = None  # Set to a number to limit frames, None for unlimited
    CONSUMER_ID = "camera1_process_saver"  # Consumer config ID
    
    logger.info("=== Frame to Image Saver Started ===")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Consumer ID: {CONSUMER_ID}")
    logger.info(f"Max frames: {MAX_FRAMES if MAX_FRAMES else 'Unlimited'}")
    
    # Create and start frame saver
    saver = FrameToImageSaver(
        output_dir=OUTPUT_DIR,
        max_frames=MAX_FRAMES
    )
    
    saver.start_saving(consumer_id=CONSUMER_ID)


if __name__ == "__main__":
    main()