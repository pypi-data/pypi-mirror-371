"""MCP 服务器实现

基于 MCP 协议实现视频分析服务器，提供多种视频分析工具。
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from loguru import logger

from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import mcp.server.stdio

from ..video_analyzer.analyzer import get_analyzer
from ..config.settings import get_settings


class VideoMCPServer:
    """视频 MCP 服务器"""

    def __init__(self):
        """初始化服务器"""
        self.settings = get_settings()
        self.analyzer = get_analyzer()
        self.server = Server("video-mcp-server")

        # 注册工具
        self._register_tools()

        logger.info("Video MCP Server 初始化完成")

    def _register_tools(self):
        """注册 MCP 工具"""

        @self.server.tool()
        async def analyze_video(args: Dict[str, Any]) -> List[TextContent]:
            """基础视频分析工具

            Args:
                video_url: 视频文件URL
                question: 分析问题
                fps: 抽帧频率（可选）
            """
            try:
                video_url = args.get("video_url")
                question = args.get("question", "这段视频的内容是什么?")
                fps = args.get("fps")

                if not video_url:
                    raise ValueError("video_url 参数是必需的")

                logger.info(f"执行视频分析: {video_url}")

                result = self.analyzer.analyze_video_basic(
                    video_url=video_url,
                    question=question,
                    fps=fps
                )

                return [TextContent(type="text", text=result)]

            except Exception as e:
                error_msg = f"视频分析失败: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=f"错误: {error_msg}")]

        @self.server.tool()
        async def analyze_video_summary(args: Dict[str, Any]) -> List[TextContent]:
            """视频摘要分析工具"""
            try:
                video_url = args.get("video_url")

                if not video_url:
                    raise ValueError("video_url 参数是必需的")

                logger.info(f"执行视频摘要分析: {video_url}")

                result = self.analyzer.analyze_video_summary(video_url)

                return [TextContent(type="text", text=result)]

            except Exception as e:
                error_msg = f"视频摘要分析失败: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=f"错误: {error_msg}")]

        @self.server.tool()
        async def analyze_video_scenes(args: Dict[str, Any]) -> List[TextContent]:
            """视频场景分析工具"""
            try:
                video_url = args.get("video_url")

                if not video_url:
                    raise ValueError("video_url 参数是必需的")

                logger.info(f"执行视频场景分析: {video_url}")

                result = self.analyzer.analyze_video_scenes(video_url)

                return [TextContent(type="text", text=result)]

            except Exception as e:
                error_msg = f"视频场景分析失败: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=f"错误: {error_msg}")]

        @self.server.tool()
        async def analyze_video_custom_prompt(args: Dict[str, Any]) -> List[TextContent]:
            """自定义提示词视频分析工具

            Args:
                video_url: 视频文件URL
                prompt_template: 提示词模板
                prompt_params: 提示词参数（JSON格式）
            """
            try:
                video_url = args.get("video_url")
                prompt_template = args.get("prompt_template")
                prompt_params_str = args.get("prompt_params", "{}")

                if not video_url:
                    raise ValueError("video_url 参数是必需的")
                if not prompt_template:
                    raise ValueError("prompt_template 参数是必需的")

                # 解析提示词参数
                try:
                    prompt_params = json.loads(prompt_params_str) if prompt_params_str else {}
                except json.JSONDecodeError as e:
                    raise ValueError(f"prompt_params 格式错误: {e}")

                logger.info(f"执行自定义提示词分析: {video_url}")

                result = self.analyzer.analyze_video_with_prompt(
                    video_url=video_url,
                    prompt_template=prompt_template,
                    **prompt_params
                )

                return [TextContent(type="text", text=result)]

            except Exception as e:
                error_msg = f"自定义提示词分析失败: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=f"错误: {error_msg}")]

    async def run(self):
        """运行服务器"""
        try:
            logger.info("启动 Video MCP Server...")

            # 使用标准输入输出接口
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )

        except Exception as e:
            logger.error(f"服务器运行失败: {e}")
            raise


# 全局服务器实例
server_instance: Optional[VideoMCPServer] = None


def get_server() -> VideoMCPServer:
    """获取服务器实例"""
    global server_instance
    if server_instance is None:
        server_instance = VideoMCPServer()
    return server_instance


async def main():
    """主函数"""
    server = get_server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())