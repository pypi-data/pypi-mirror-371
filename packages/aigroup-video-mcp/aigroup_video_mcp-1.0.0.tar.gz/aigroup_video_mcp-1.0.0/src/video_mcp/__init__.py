"""Video MCP Service - 基于阿里云 DashScope 的视频多模态理解 MCP 服务器

这是一个可通过 pip 安装的 Python 包，提供视频分析的 MCP 服务功能。
支持通过标准输入输出(stdio)模式运行 MCP 服务器。
"""

__version__ = "1.0.0"
__author__ = "Video MCP Team"
__description__ = "基于阿里云 DashScope 的视频多模态理解 MCP 服务器"

from .config.settings import get_settings
from .mcp_server.server import get_server
from .video_analyzer.analyzer import get_analyzer

__all__ = ["get_settings", "get_server", "get_analyzer"]