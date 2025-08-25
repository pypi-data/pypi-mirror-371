"""命令行接口

提供命令行工具来运行 Video MCP 服务器。
"""

import asyncio
import sys
import os
from pathlib import Path
from loguru import logger

from .config.settings import get_settings, create_directories
from .mcp_server.server import main as server_main


def setup_logging():
    """设置日志"""
    settings = get_settings()

    # 创建日志目录
    create_directories()

    # 配置日志
    log_file = settings.log_dir / "video_mcp_server.log"
    logger.add(
        log_file,
        rotation="10 MB",
        retention="30 days",
        level=settings.server.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}"
    )

    # 控制台日志
    logger.add(
        sys.stderr,
        level=settings.server.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    )


def check_environment():
    """检查环境配置"""
    settings = get_settings()

    # 检查 API Key
    if not settings.dashscope.api_key:
        logger.error("错误: DASHSCOPE_API_KEY 未配置")
        logger.info("请在 .env 文件中设置 DASHSCOPE_API_KEY")
        return False

    logger.info("环境配置检查通过")
    logger.info(f"使用模型: {settings.dashscope.model}")
    logger.info(f"服务器配置: {settings.server.host}:{settings.server.port}")

    return True


def main():
    """主入口函数"""
    try:
        # 设置日志
        setup_logging()

        logger.info("启动 Video MCP Server...")

        # 检查环境
        if not check_environment():
            sys.exit(1)

        # 启动服务器
        asyncio.run(server_main())

    except KeyboardInterrupt:
        logger.info("服务器被用户中断")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()