"""视频分析器

基于原始 1.py 文件的逻辑，封装 DashScope API 调用功能。
提供视频内容分析、摘要、场景识别等功能。
"""

import os
import dashscope
from typing import Dict, List, Optional, Any
from loguru import logger
from urllib.parse import urlparse

from ..config.settings import get_settings


class VideoAnalyzer:
    """视频分析器类"""

    def __init__(self):
        """初始化视频分析器"""
        self.settings = get_settings()
        self._setup_dashscope()

    def _setup_dashscope(self):
        """配置 DashScope 客户端"""
        try:
            api_key = self.settings.dashscope.api_key
            if not api_key:
                raise ValueError("DashScope API Key 未配置")

            # DashScope 库会自动从环境变量读取 API Key
            os.environ['DASHSCOPE_API_KEY'] = api_key
            logger.info("DashScope 客户端配置成功")

        except Exception as e:
            logger.error(f"DashScope 客户端配置失败: {e}")
            raise

    def _validate_video_url(self, video_url: str) -> bool:
        """验证视频URL格式"""
        try:
            if not video_url:
                return False
            parsed = urlparse(video_url)
            # 只允许 http 和 https 协议
            return bool(parsed.scheme in ['http', 'https'] and parsed.netloc)
        except Exception:
            return False

    def _create_base_message(self, video_url: str, text_prompt: str, fps: float = None) -> List[Dict]:
        """创建基础消息结构"""
        if not self._validate_video_url(video_url):
            raise ValueError(f"无效的视频URL: {video_url}")

        fps_value = fps or self.settings.video.default_fps

        messages = [
            {
                "role": "system",
                "content": [{"text": "You are a helpful video analysis assistant."}]
            },
            {
                "role": "user",
                "content": [
                    {
                        "video": video_url,
                        "fps": fps_value
                    },
                    {
                        "text": text_prompt
                    }
                ]
            }
        ]

        return messages

    def analyze_video_basic(self, video_url: str, question: str, fps: float = None) -> str:
        """基础视频分析 - 基于原始 1.py 的逻辑

        Args:
            video_url: 视频文件URL
            question: 分析问题
            fps: 抽帧频率，默认使用配置值

        Returns:
            分析结果文本
        """
        try:
            logger.info(f"开始分析视频: {video_url}")
            logger.debug(f"问题: {question}")

            messages = self._create_base_message(video_url, question, fps)

            response = dashscope.MultiModalConversation.call(
                model=self.settings.dashscope.model,
                messages=messages,
                max_tokens=self.settings.dashscope.max_tokens,
                temperature=self.settings.dashscope.temperature
            )

            if response.status_code != 200:
                error_msg = f"API调用失败: {response.status_code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)

            result = response.output.choices[0].message.content[0]["text"]
            logger.info("视频分析完成")
            return result

        except Exception as e:
            logger.error(f"视频分析失败: {e}")
            raise

    def analyze_video_with_prompt(self, video_url: str, prompt_template: str, **kwargs) -> str:
        """使用提示词模板分析视频

        Args:
            video_url: 视频文件URL
            prompt_template: 提示词模板
            **kwargs: 模板参数

        Returns:
            分析结果文本
        """
        try:
            # 格式化提示词
            question = prompt_template.format(**kwargs) if kwargs else prompt_template

            logger.info(f"使用提示词模板分析视频: {prompt_template[:50]}...")
            return self.analyze_video_basic(video_url, question)

        except Exception as e:
            logger.error(f"提示词分析失败: {e}")
            raise

    def analyze_video_summary(self, video_url: str) -> str:
        """视频摘要分析"""
        prompt = "请提供这个视频的详细摘要，包括主要内容、场景、人物和关键事件。"
        return self.analyze_video_with_prompt(video_url, prompt)

    def analyze_video_scenes(self, video_url: str) -> str:
        """视频场景分析"""
        prompt = "请分析这个视频中的主要场景和场景转换，并描述每个场景的内容。"
        return self.analyze_video_with_prompt(video_url, prompt)

    def analyze_video_content(self, video_url: str, custom_question: str) -> str:
        """自定义问题分析视频"""
        return self.analyze_video_basic(video_url, custom_question)


# 全局分析器实例 - 懒加载
_analyzer_instance: Optional[VideoAnalyzer] = None


def get_analyzer() -> VideoAnalyzer:
    """获取视频分析器实例"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = VideoAnalyzer()
    return _analyzer_instance