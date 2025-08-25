"""配置管理模块

使用 Pydantic 提供类型安全的配置管理，支持环境变量和配置文件。
"""

import os
from typing import Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path


class DashScopeConfig(BaseSettings):
    """DashScope API 配置"""

    api_key: Optional[str] = Field(default=None, description="DashScope API Key")
    model: str = Field(default="qwen-vl-max-latest", description="使用的模型名称")
    max_tokens: int = Field(default=2048, description="最大输出 token 数")
    temperature: float = Field(default=0.7, description="生成温度")

    model_config = ConfigDict(env_prefix="DASHSCOPE_")


class VideoConfig(BaseSettings):
    """视频处理配置"""

    max_duration: int = Field(default=600, description="最大视频时长(秒)")
    default_fps: float = Field(default=2.0, description="默认抽帧频率")
    supported_formats: list[str] = Field(
        default=["mp4", "avi", "mov", "mkv", "webm"],
        description="支持的视频格式"
    )
    max_file_size: int = Field(default=100 * 1024 * 1024, description="最大文件大小(字节)")


class ServerConfig(BaseSettings):
    """服务器配置"""

    host: str = Field(default="127.0.0.1", description="服务器主机地址")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")
    log_level: str = Field(default="INFO", description="日志级别")


class Settings(BaseSettings):
    """全局配置"""

    # 基础配置
    project_name: str = "Video MCP Service"
    version: str = "1.0.0"
    debug: bool = Field(default=False)

    # 模块配置
    dashscope: DashScopeConfig = DashScopeConfig()
    video: VideoConfig = VideoConfig()
    server: ServerConfig = ServerConfig()

    # 路径配置
    base_dir: Path = Path(__file__).parent.parent.parent
    log_dir: Path = base_dir / "logs"
    temp_dir: Path = base_dir / "temp"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        # 从环境变量获取 DEBUG 设置
        if "debug" not in kwargs and "DEBUG" in os.environ:
            kwargs["debug"] = os.environ["DEBUG"].lower() in ("true", "1", "yes")

        super().__init__(**kwargs)


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def create_directories():
    """创建必要的目录"""
    settings.log_dir.mkdir(exist_ok=True)
    settings.temp_dir.mkdir(exist_ok=True)