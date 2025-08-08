# 引用
[https://github.com/invariantlabs-ai/mcp-streamable-http](https://github.com/invariantlabs-ai/mcp-streamable-http) 基于这个改成基于Openai的模式

# MCP Client Server Python

这是一个基于 MCP (Model Context Protocol) 的客户端-服务器项目，使用 Python 实现。项目包含一个天气服务服务器和一个支持 OpenAI 兼容 API 的客户端。

## 项目结构

```
mcp_client_server_python/
├── client/                 # MCP 客户端
│   ├── client.py          # 主客户端代码
│   ├── test_client.py     # 测试脚本
│   ├── pyproject.toml     # 客户端依赖配置
│   └── env_config.txt     # 环境变量配置示例
├── server/                 # MCP 服务器
│   ├── weather.py         # 天气服务服务器
│   └── pyproject.toml     # 服务器依赖配置
├── .gitignore             # Git 忽略文件
└── README.md              # 项目说明文档
```

## 功能特性

### 服务器端 (Weather Server)
- 提供天气查询工具
- 支持获取美国各州的天气警报
- 支持根据经纬度获取天气预报
- 使用 NWS (National Weather Service) API

### 客户端 (MCP Client)
- 支持 OpenAI 兼容的 API
- 自动处理工具调用
- 支持环境变量配置
- 交互式聊天界面

## 安装和配置

### 1. 克隆项目
```bash
git clone <repository-url>
cd mcp_client_server_python
```

### 2. 安装服务器依赖
```bash
cd server
pip install -e .
```

### 3. 安装客户端依赖
```bash
cd ../client
pip install -e .
```

### 4. 配置环境变量
在 `client` 目录下创建 `.env` 文件：
```bash
cp env_config.txt .env
```

编辑 `.env` 文件，填入你的配置：
```env
OPENAI_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

## 使用方法

### 启动服务器
```bash
cd server
python weather.py --port 8123
```

### 启动客户端
```bash
cd client
python client.py --mcp-localhost-port 8123
```

### 测试客户端连接
```bash
cd client
python test_client.py
```

## 示例用法

### 天气查询示例
```
Query: What's the weather like in New York City?
```

### 天气警报查询示例
```
Query: Are there any weather alerts in California?
```

## 技术栈

- **MCP**: Model Context Protocol 用于客户端-服务器通信
- **FastMCP**: 快速 MCP 服务器框架
- **httpx**: 异步 HTTP 客户端
- **uvicorn**: ASGI 服务器
- **python-dotenv**: 环境变量管理

## 依赖版本

### 服务器依赖
- `httpx~=0.28.0`
- `mcp~=1.9.0`
- `uvicorn~=0.27.0`

### 客户端依赖
- `httpx>=0.25.0`
- `mcp>=1.9.0`
- `python-dotenv~=1.1.0`

## 开发说明

### 解决依赖冲突
项目使用 `httpx` 替代 `openai` 库来避免 `anyio` 版本冲突问题。

### 环境变量配置
- `OPENAI_KEY`: OpenAI API 密钥
- `OPENAI_BASE_URL`: OpenAI 兼容 API 的基础 URL

### 支持的 API 端点
- OpenAI API: `https://api.openai.com/v1`
- 本地模型: `http://localhost:11434/v1`
- 其他兼容端点


### dify MCP
<img width="2776" height="1184" alt="image" src="https://github.com/user-attachments/assets/579317ed-dfb6-4790-aa5f-c260bedf9e64" />


## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 
