# Video MCP - 基于阿里云 DashScope 的视频多模态理解 MCP 服务器

基于阿里云 DashScope 的视频多模态理解 MCP 服务器，提供强大的视频内容分析功能。

## 🚀 特性

- 🎥 **视频内容分析**: 支持通过URL分析视频内容
- 📝 **智能摘要**: 自动生成视频摘要和关键信息
- 🎬 **场景识别**: 识别视频中的主要场景和场景转换
- 🔧 **自定义提示词**: 支持灵活的自定义分析需求
- 🛠️ **MCP协议**: 完全兼容MCP协议，支持 stdio 模式运行
- ⚡ **高性能**: 基于异步处理，支持并发请求
- 📦 **pip安装**: 可通过 pip 直接安装和使用
- 🧪 **完整测试**: 提供全面的单元测试覆盖
- 📊 **详细日志**: 完整的日志记录和错误处理

## 📋 环境要求

- Python 3.8+
- 有效的 DashScope API Key

## 🛠️ 安装

### 方法一：从 PyPI 安装（推荐）

```bash
pip install video-mcp
```

### 方法二：从源码安装

1. **克隆项目**
    ```bash
    git clone <repository-url>
    cd video-mcp
    ```

2. **安装依赖**
    ```bash
    pip install -e .
    # 或者安装开发依赖
    pip install -e ".[dev]"
    ```

3. **配置环境变量**
    ```bash
    cp .env.example .env
    # 编辑 .env 文件，填入你的 DashScope API Key
    ```

## ⚙️ 配置

在 `.env` 文件中配置以下参数：

```env
# 必需配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 可选配置
DASHSCOPE_MODEL=qwen-vl-max-latest
DASHSCOPE_MAX_TOKENS=2048
DASHSCOPE_TEMPERATURE=0.7

VIDEO_MAX_DURATION=600
VIDEO_DEFAULT_FPS=2.0
VIDEO_MAX_FILE_SIZE=104857600

SERVER_HOST=127.0.0.1
SERVER_PORT=8000
SERVER_WORKERS=1
LOG_LEVEL=INFO
```

## 🚀 使用方法

### 1. 命令行启动（推荐）

安装完成后，可以直接使用 `video-mcp` 命令启动服务器：

```bash
# 启动 MCP 服务器
video-mcp
```

### 2. 作为MCP工具使用

服务器启动后，可以通过MCP协议调用以下工具：

#### 基础视频分析
```python
{
  "method": "tools/call",
  "params": {
    "name": "analyze_video",
    "arguments": {
      "video_url": "https://example.com/video.mp4",
      "question": "这段视频的主要内容是什么？",
      "fps": 2.0
    }
  }
}
```

#### 视频摘要分析
```python
{
  "method": "tools/call",
  "params": {
    "name": "analyze_video_summary",
    "arguments": {
      "video_url": "https://example.com/video.mp4"
    }
  }
}
```

#### 视频场景分析
```python
{
  "method": "tools/call",
  "params": {
    "name": "analyze_video_scenes",
    "arguments": {
      "video_url": "https://example.com/video.mp4"
    }
  }
}
```

#### 自定义提示词分析
```python
{
  "method": "tools/call",
  "params": {
    "name": "analyze_video_custom_prompt",
    "arguments": {
      "video_url": "https://example.com/video.mp4",
      "prompt_template": "请分析这个视频中的{subject}元素",
      "prompt_params": "{\"subject\": \"人物\"}"
    }
  }
}
```

### 3. Python API 使用

```python
from video_mcp import get_analyzer

analyzer = get_analyzer()

# 基础分析
result = analyzer.analyze_video_basic(
    video_url="https://example.com/video.mp4",
    question="这段视频的内容是什么？"
)

# 视频摘要
summary = analyzer.analyze_video_summary("https://example.com/video.mp4")

# 场景分析
scenes = analyzer.analyze_video_scenes("https://example.com/video.mp4")

# 自定义提示词
result = analyzer.analyze_video_with_prompt(
    video_url="https://example.com/video.mp4",
    prompt_template="请详细描述视频中的{topic}",
    topic="教学内容"
)
```

### 4. MCP stdio 模式集成

Video MCP 支持标准的 stdio 模式，可以直接集成到支持 MCP 的应用中：

```json
{
  "mcpServers": {
    "video-mcp": {
      "command": "video-mcp",
      "args": []
    }
  }
}
```

## 🏗️ 项目结构

```
video-mcp/
├── 📄 pyproject.toml              # 现代Python项目配置
├── 📄 setup.py                   # 兼容性安装脚本
├── 📄 MANIFEST.in                # 包文件清单
├── 📄 README.md                  # 项目文档
├── 📄 CHANGELOG.md               # 更新日志
├── 📄 LICENSE                    # 许可证
├── 📄 .env.example               # 环境变量配置模板
├── 📄 .gitignore                 # Git忽略文件配置
├── 📁 src/video_mcp/             # 主要包代码
│   ├── 📄 __init__.py            # 包初始化和公共API
│   ├── 📄 cli.py                 # 命令行接口
│   ├── 📁 config/                # 配置模块
│   │   ├── 📄 __init__.py
│   │   └── 📄 settings.py        # 统一配置管理
│   ├── 📁 mcp_server/            # MCP服务器模块
│   │   ├── 📄 __init__.py
│   │   └── 📄 server.py          # MCP服务核心实现
│   └── 📁 video_analyzer/        # 视频分析模块
│       ├── 📄 __init__.py
│       └── 📄 analyzer.py        # 视频分析核心逻辑
└── 📁 tests/                     # 测试目录
    ├── 📄 __init__.py
    └── 📄 test_video_analyzer.py # 视频分析器单元测试
```

## 🧪 测试

运行单元测试：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_video_analyzer.py

# 运行带覆盖率测试
pytest --cov=video_mcp --cov-report=html
```

## 🔧 开发

### 代码格式化
```bash
# 使用 black 格式化代码
black src/ tests/

# 使用 isort 整理导入
isort src/ tests/

# 使用 flake8 检查代码风格
flake8 src/ tests/
```

### 类型检查
```bash
mypy src/
```

## 📝 日志

日志文件保存在 `logs/` 目录下，包含详细的运行信息和错误记录。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [阿里云 DashScope](https://help.aliyun.com/zh/model-studio/) - 提供强大的多模态理解能力
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - 提供 MCP 协议支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/your-repo/video-mcp/issues)
- 发送邮件至项目维护者

---

**注意**: 请确保遵守阿里云 DashScope 的使用条款和服务协议。