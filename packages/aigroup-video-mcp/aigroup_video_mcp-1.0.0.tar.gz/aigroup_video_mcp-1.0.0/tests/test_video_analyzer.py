"""视频分析器单元测试

测试 VideoAnalyzer 类的各项功能，包括基础分析、摘要分析、场景分析等。
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.video_analyzer.analyzer import VideoAnalyzer
from src.config.settings import Settings


class TestVideoAnalyzer:
    """视频分析器测试类"""

    @pytest.fixture
    def mock_settings(self):
        """模拟配置"""
        settings = MagicMock(spec=Settings)

        # 创建 dashscope 配置的 mock
        mock_dashscope = MagicMock()
        mock_dashscope.api_key = "test_api_key"
        mock_dashscope.model = "qwen-vl-max-latest"
        mock_dashscope.max_tokens = 2048
        mock_dashscope.temperature = 0.7

        # 创建 video 配置的 mock
        mock_video = MagicMock()
        mock_video.default_fps = 2.0

        # 设置嵌套属性
        settings.dashscope = mock_dashscope
        settings.video = mock_video

        return settings

    @pytest.fixture
    def analyzer(self, mock_settings):
        """创建测试分析器实例"""
        with patch('src.video_analyzer.analyzer.get_settings', return_value=mock_settings):
            with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'test_api_key'}):
                return VideoAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert analyzer.settings is not None

    def test_validate_video_url_valid(self, analyzer):
        """测试有效视频URL验证"""
        valid_urls = [
            "https://example.com/video.mp4",
            "http://example.com/video.avi",
            "https://example.com/path/to/video.mov"
        ]

        for url in valid_urls:
            assert analyzer._validate_video_url(url) is True

    def test_validate_video_url_invalid(self, analyzer):
        """测试无效视频URL验证"""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com/video.mp4",
            "",
            None
        ]

        for url in invalid_urls:
            assert analyzer._validate_video_url(url) is False

    def test_create_base_message(self, analyzer):
        """测试基础消息创建"""
        video_url = "https://example.com/video.mp4"
        text_prompt = "测试问题"
        fps = 1.0

        messages = analyzer._create_base_message(video_url, text_prompt, fps)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"][0]["video"] == video_url
        assert messages[1]["content"][0]["fps"] == fps
        assert messages[1]["content"][1]["text"] == text_prompt

    def test_create_base_message_default_fps(self, analyzer, mock_settings):
        """测试使用默认FPS创建消息"""
        video_url = "https://example.com/video.mp4"
        text_prompt = "测试问题"

        messages = analyzer._create_base_message(video_url, text_prompt)

        assert messages[1]["content"][0]["fps"] == mock_settings.video.default_fps

    def test_create_base_message_invalid_url(self, analyzer):
        """测试无效URL时的错误处理"""
        with pytest.raises(ValueError, match="无效的视频URL"):
            analyzer._create_base_message("invalid_url", "测试问题")

    @patch('dashscope.MultiModalConversation.call')
    def test_analyze_video_basic_success(self, mock_call, analyzer):
        """测试基础视频分析成功情况"""
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        # 正确设置嵌套的 mock 结构
        mock_output = MagicMock()
        mock_choices = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_text_item = MagicMock()

        mock_text_item.__getitem__ = lambda self, key: "分析结果" if key == "text" else None
        mock_content.__getitem__ = lambda self, index: mock_text_item if index == 0 else None
        mock_message.content = mock_content
        mock_choice.message = mock_message
        mock_choices.__getitem__ = lambda self, index: mock_choice if index == 0 else None
        mock_output.choices = mock_choices
        mock_response.output = mock_output

        mock_call.return_value = mock_response

        result = analyzer.analyze_video_basic(
            video_url="https://example.com/video.mp4",
            question="测试问题"
        )

        assert result == "分析结果"
        mock_call.assert_called_once()

    @patch('dashscope.MultiModalConversation.call')
    def test_analyze_video_basic_api_error(self, mock_call, analyzer):
        """测试API调用失败的情况"""
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.message = "API Error"
        mock_call.return_value = mock_response

        with pytest.raises(Exception, match="API调用失败"):
            analyzer.analyze_video_basic(
                video_url="https://example.com/video.mp4",
                question="测试问题"
            )

    def test_analyze_video_summary(self, analyzer):
        """测试视频摘要分析"""
        with patch.object(analyzer, 'analyze_video_with_prompt') as mock_analyze:
            mock_analyze.return_value = "摘要结果"

            result = analyzer.analyze_video_summary("https://example.com/video.mp4")

            assert result == "摘要结果"
            mock_analyze.assert_called_once()
            # 检查是否调用了 analyze_video_with_prompt，参数是固定的提示词
            call_args = mock_analyze.call_args[0]
            assert len(call_args) >= 2  # 至少有 video_url 和 prompt_template 参数
            prompt_arg = call_args[1]  # 第二个参数是 prompt_template
            assert "摘要" in prompt_arg

    def test_analyze_video_scenes(self, analyzer):
        """测试视频场景分析"""
        with patch.object(analyzer, 'analyze_video_with_prompt') as mock_analyze:
            mock_analyze.return_value = "场景分析结果"

            result = analyzer.analyze_video_scenes("https://example.com/video.mp4")

            assert result == "场景分析结果"
            mock_analyze.assert_called_once()
            # 检查是否调用了 analyze_video_with_prompt，参数是固定的提示词
            call_args = mock_analyze.call_args[0]
            assert len(call_args) >= 2  # 至少有 video_url 和 prompt_template 参数
            prompt_arg = call_args[1]  # 第二个参数是 prompt_template
            assert "场景" in prompt_arg

    def test_analyze_video_content(self, analyzer):
        """测试自定义问题分析"""
        with patch.object(analyzer, 'analyze_video_basic') as mock_analyze:
            mock_analyze.return_value = "自定义分析结果"

            result = analyzer.analyze_video_content(
                "https://example.com/video.mp4",
                "自定义问题"
            )

            assert result == "自定义分析结果"
            # analyze_video_content 调用 analyze_video_basic 时使用位置参数
            mock_analyze.assert_called_once_with(
                "https://example.com/video.mp4",
                "自定义问题"
            )

    def test_analyze_video_with_prompt(self, analyzer):
        """测试提示词模板分析"""
        with patch.object(analyzer, 'analyze_video_basic') as mock_analyze:
            mock_analyze.return_value = "模板分析结果"

            prompt_template = "请分析{subject}的内容"
            result = analyzer.analyze_video_with_prompt(
                "https://example.com/video.mp4",
                prompt_template,
                subject="视频"
            )

            assert result == "模板分析结果"
            # analyze_video_with_prompt 调用 analyze_video_basic 时使用位置参数
            mock_analyze.assert_called_once_with(
                "https://example.com/video.mp4",
                "请分析视频的内容"
            )

    def test_analyzer_initialization_no_api_key(self):
        """测试缺少API Key时的初始化失败"""
        settings = MagicMock(spec=Settings)

        # 创建 dashscope 配置的 mock，API key 为 None
        mock_dashscope = MagicMock()
        mock_dashscope.api_key = None
        mock_dashscope.model = "qwen-vl-max-latest"
        mock_dashscope.max_tokens = 2048
        mock_dashscope.temperature = 0.7

        # 创建 video 配置的 mock
        mock_video = MagicMock()
        mock_video.default_fps = 2.0

        # 设置嵌套属性
        settings.dashscope = mock_dashscope
        settings.video = mock_video

        with patch('src.video_analyzer.analyzer.get_settings', return_value=settings):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="DashScope API Key 未配置"):
                    VideoAnalyzer()