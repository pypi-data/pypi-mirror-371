"""项目安装脚本"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README 文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取版本信息
def get_version():
    """从 __init__.py 文件读取版本信息"""
    init_file = this_directory / "src" / "video_mcp" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text(encoding='utf-8')
        for line in content.split('\n'):
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    name="video-mcp",
    version=get_version(),
    author="Video MCP Team",
    author_email="",
    description="基于阿里云 DashScope 的视频多模态理解 MCP 服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/video-mcp",
    packages=find_packages(where="src", exclude=["tests*"]),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video :: Analysis",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=0.1.0",
        "dashscope>=1.20.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "loguru>=0.7.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "typing-extensions>=4.0.0;python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "video-mcp=video_mcp.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.yml", "*.yaml"],
    },
    keywords="video analysis multimodal dashscope mcp server ai computer-vision",
    project_urls={
        "Documentation": "https://github.com/your-repo/video-mcp#readme",
        "Source": "https://github.com/your-repo/video-mcp",
        "Tracker": "https://github.com/your-repo/video-mcp/issues",
        "Changelog": "https://github.com/your-repo/video-mcp/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
)