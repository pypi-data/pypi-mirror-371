#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka Topic 连通性测试脚本
用于测试 camera1.video.jpeg.process.v1.dev topic 的数据获取
"""

import sys
from pathlib import Path
import time
import json
from datetime import datetime
from typing import Dict, Any
import cv2
import numpy as np

# 添加项目根目录到 Python 路径
current_file = Path(__file__)
src_dir = current_file.parent.parent  # 回到 src 目录
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from soa_kafka_python.utils.consumers.consumers import VideoFrameConsumer
from soa_kafka_python.utils.common_utils import _log, config_loader

logger = _log()
config_dict = config_loader()


class Camera1TopicTester:
    """
    Camera1 视频 Topic 连通性测试类
    专门用于测试 camera1.video.jpeg.process.v1.dev topic 的数据获取
    """
    
    def __init__(self, test_duration: int = 30, max_frames: int = 10):
        """
        初始化测试器
        
        Args:
            test_duration: 测试持续时间（秒）
            max_frames: 最大测试帧数
        """
        self.test_duration = test_duration
        self.max_frames = max_frames
        self.received_count = 0
        self.start_time = None
        self.test_results = {
            'connection_status': 'unknown',
            'total_frames_received': 0,
            'test_duration': 0,
            'average_fps': 0,
            'first_frame_time': None,
            'last_frame_time': None,
            'frame_details': [],
            'errors': []
        }
        
        # 从配置中获取 topic 信息
        self.consumer_config = config_dict['consumers_configs']['camera1_process_saver']
        self.target_topic = self.consumer_config['sub_topic']
        
        logger.info(f"初始化 Camera1 Topic 测试器")
        logger.info(f"目标 Topic: {self.target_topic}")
        logger.info(f"测试时长: {test_duration} 秒")
        logger.info(f"最大帧数: {max_frames}")
    
    def frame_processor(self, frame: np.ndarray, timestamp: float, metadata: Dict[str, Any] = None) -> None:
        """
        处理接收到的视频帧
        
        Args:
            frame: 视频帧数据
            timestamp: 时间戳
            metadata: 元数据
        """
        try:
            self.received_count += 1
            current_time = time.time()
            
            # 记录第一帧时间
            if self.received_count == 1:
                self.test_results['first_frame_time'] = current_time
                self.test_results['connection_status'] = 'connected'
                logger.info("🎉 成功连接到 Kafka Topic！")
            
            # 更新最后一帧时间
            self.test_results['last_frame_time'] = current_time
            
            # 记录帧详情
            frame_info = {
                'frame_number': self.received_count,
                'timestamp': timestamp,
                'receive_time': current_time,
                'frame_shape': frame.shape if frame is not None else None,
                'frame_size_bytes': frame.nbytes if frame is not None else 0
            }
            
            # 添加元数据信息
            if metadata:
                frame_info.update({
                    'video_width': metadata.get('video_width'),
                    'video_height': metadata.get('video_height'),
                    'video_channels': metadata.get('video_channels'),
                    'video_source': metadata.get('video_source'),
                    'frame_id': metadata.get('frame_id'),
                    'source_attributes': metadata.get('source_attributes')
                })
            
            self.test_results['frame_details'].append(frame_info)
            
            # 实时显示接收状态
            elapsed = current_time - self.start_time
            fps = self.received_count / elapsed if elapsed > 0 else 0
            
            logger.info(f"📺 帧 #{self.received_count:03d} | "
                       f"时间戳: {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]} | "
                       f"形状: {frame.shape} | "
                       f"大小: {frame.nbytes/1024:.1f}KB | "
                       f"FPS: {fps:.2f}")
            
            # 显示元数据（仅前几帧）
            if self.received_count <= 3 and metadata:
                logger.info(f"   📋 元数据: 源={metadata.get('video_source', 'N/A')}, "
                           f"分辨率={metadata.get('video_width', 'N/A')}x{metadata.get('video_height', 'N/A')}, "
                           f"帧ID={metadata.get('frame_id', 'N/A')}")
            
            # 检查是否达到最大帧数
            if self.received_count >= self.max_frames:
                logger.info(f"✅ 已达到最大测试帧数: {self.max_frames}")
                return
                
        except Exception as e:
            error_msg = f"处理帧时出错: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append({
                'timestamp': time.time(),
                'error': error_msg,
                'frame_number': self.received_count
            })
    
    def run_connectivity_test(self) -> Dict[str, Any]:
        """
        运行连通性测试
        
        Returns:
            Dict[str, Any]: 测试结果
        """
        logger.info("="*80)
        logger.info("🚀 开始 Camera1 Topic 连通性测试")
        logger.info("="*80)
        
        self.start_time = time.time()
        
        try:
            # 创建视频帧消费者
            consumer = VideoFrameConsumer(
                consumer_id="camera1_process_saver",
                frame_processor=self.frame_processor
            )
            
            logger.info(f"📡 正在连接到 Topic: {self.target_topic}")
            logger.info(f"⏱️  测试将运行 {self.test_duration} 秒或直到接收到 {self.max_frames} 帧")
            logger.info(f"🔄 开始消费数据...")
            
            # 设置超时时间
            timeout_time = self.start_time + self.test_duration
            
            # 开始消费，但限制时间和帧数
            consumer.consume_frames(max_frames=self.max_frames, timeout=1.0)
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  用户中断测试")
        except Exception as e:
            error_msg = f"测试过程中出现错误: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.test_results['errors'].append({
                'timestamp': time.time(),
                'error': error_msg,
                'type': 'consumer_error'
            })
            self.test_results['connection_status'] = 'error'
        
        # 计算测试结果
        end_time = time.time()
        actual_duration = end_time - self.start_time
        
        self.test_results.update({
            'total_frames_received': self.received_count,
            'test_duration': actual_duration,
            'average_fps': self.received_count / actual_duration if actual_duration > 0 else 0
        })
        
        # 如果没有接收到任何帧，标记为连接失败
        if self.received_count == 0:
            self.test_results['connection_status'] = 'failed'
        
        return self.test_results
    
    def print_test_summary(self, results: Dict[str, Any]) -> None:
        """
        打印测试结果摘要
        
        Args:
            results: 测试结果字典
        """
        logger.info("\n" + "="*80)
        logger.info("📊 测试结果摘要")
        logger.info("="*80)
        
        # 连接状态
        status_emoji = {
            'connected': '✅',
            'failed': '❌',
            'error': '⚠️',
            'unknown': '❓'
        }
        
        status = results['connection_status']
        logger.info(f"🔗 连接状态: {status_emoji.get(status, '❓')} {status.upper()}")
        
        # 基本统计
        logger.info(f"📺 接收帧数: {results['total_frames_received']}")
        logger.info(f"⏱️  测试时长: {results['test_duration']:.2f} 秒")
        logger.info(f"📈 平均 FPS: {results['average_fps']:.2f}")
        
        # 时间信息
        if results['first_frame_time']:
            first_time = datetime.fromtimestamp(results['first_frame_time']).strftime('%H:%M:%S.%f')[:-3]
            logger.info(f"🕐 首帧时间: {first_time}")
        
        if results['last_frame_time']:
            last_time = datetime.fromtimestamp(results['last_frame_time']).strftime('%H:%M:%S.%f')[:-3]
            logger.info(f"🕐 末帧时间: {last_time}")
        
        # 错误信息
        if results['errors']:
            logger.info(f"\n⚠️  发现 {len(results['errors'])} 个错误:")
            for i, error in enumerate(results['errors'][:5], 1):  # 只显示前5个错误
                logger.info(f"   {i}. {error['error']}")
            if len(results['errors']) > 5:
                logger.info(f"   ... 还有 {len(results['errors']) - 5} 个错误")
        
        # 连通性结论
        logger.info("\n" + "-"*80)
        if status == 'connected' and results['total_frames_received'] > 0:
            logger.info("🎉 连通性测试成功！Topic 数据流正常。")
        elif status == 'failed':
            logger.info("❌ 连通性测试失败！无法接收到数据。")
            logger.info("💡 请检查:")
            logger.info("   - Kafka 服务是否运行")
            logger.info("   - Topic 是否存在")
            logger.info("   - 生产者是否在发送数据")
            logger.info("   - 网络连接是否正常")
        else:
            logger.info("⚠️  连通性测试出现异常，请查看错误信息。")
        
        logger.info("="*80)


def main():
    """
    主函数
    """
    # 测试配置
    TEST_DURATION = 30  # 测试持续时间（秒）
    MAX_FRAMES = 20     # 最大测试帧数
    
    try:
        # 创建测试器
        tester = Camera1TopicTester(
            test_duration=TEST_DURATION,
            max_frames=MAX_FRAMES
        )
        
        # 运行测试
        results = tester.run_connectivity_test()
        
        # 打印结果
        tester.print_test_summary(results)
        
        # 保存结果到文件（可选）
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        logger.info(f"📄 详细结果已保存到: {results_file}")
        
    except Exception as e:
        logger.error(f"❌ 测试脚本执行失败: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())