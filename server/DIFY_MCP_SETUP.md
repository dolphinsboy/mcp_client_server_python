# Dify MCP 授权配置指南

## 概述

这个 Weather MCP 服务器已经配置为支持 Dify MCP 授权机制，确保只有经过授权的客户端才能访问天气工具。

## 功能特性

- 🔐 **Bearer Token 认证**: 使用 API Key 进行身份验证
- 🏥 **健康检查端点**: `/health` 端点用于服务状态监控
- 🔧 **灵活配置**: 支持环境变量和命令行参数配置
- 🛡️ **安全中间件**: 自动验证所有请求的授权头
- 📚 **API 文档**: 自动生成的 OpenAPI 文档
- ✅ **MCP 兼容**: 完全兼容 MCP (Model Context Protocol) 标准

## 安装依赖

### 方法 1: 使用 pyproject.toml (推荐)

```bash
pip install -e .
```

### 方法 2: 使用 requirements.txt

```bash
pip install -r requirements.txt
```

### 方法 3: 手动安装兼容版本

如果遇到依赖冲突，可以手动安装兼容版本：

```bash
pip install "mcp>=1.9.0" "fastapi>=0.115.0" "httpx>=0.28.0,<0.29.0" "uvicorn>=0.27.0"
```

### 方法 4: 使用安装脚本

```bash
chmod +x install.sh
./install.sh
```

## 依赖冲突解决

如果遇到 `anyio` 版本冲突，这是因为不同包对 `anyio` 版本要求不同。解决方案：

1. **使用更新的版本**: 确保使用 FastAPI >= 0.115.0 和 httpx >= 0.28.0
2. **清理环境**: 删除冲突的包并重新安装
3. **使用虚拟环境**: 创建新的虚拟环境避免冲突

```bash
# 清理并重新安装
pip uninstall fastapi httpx mcp uvicorn -y
pip install -r requirements.txt
```

## 配置方式

### 1. 环境变量配置

创建 `.env` 文件（参考 `dify_config_example.env`）：

```bash
# 复制示例配置文件
cp dify_config_example.env .env

# 编辑配置文件，设置你的 API Key
DIFY_API_KEY=your_actual_api_key_here
```

### 2. 命令行参数配置

```bash
# 使用命令行参数设置 API Key
python weather.py --api-key your_api_key_here

# 指定端口和主机
python weather.py --host 0.0.0.0 --port 8123 --api-key your_api_key_here

# 开发模式：禁用认证
python weather.py --no-auth
```

## 启动服务器

### 生产环境

```bash
# 使用环境变量
export DIFY_API_KEY=your_api_key_here
python weather.py

# 或使用命令行参数
python weather.py --api-key your_api_key_here
```

### 开发环境

```bash
# 禁用认证进行开发测试
python weather.py --no-auth
```

## 测试连接

### 使用测试脚本

```bash
# 测试 MCP 连接
python test_mcp_connection.py
```

### 手动测试

```bash
# 测试健康检查端点
curl http://localhost:8123/health

# 测试 MCP 端点
curl http://localhost:8123/mcp
```

## API 使用

### 认证

所有请求都需要在 HTTP 头中包含 Bearer Token：

```bash
curl -H "Authorization: Bearer your_api_key_here" \
     http://localhost:8123/health
```

### 健康检查

```bash
curl http://localhost:8123/health
```

响应：
```json
{
  "status": "healthy",
  "service": "weather-mcp"
}
```

### 天气工具

```bash
# 获取天气预报
curl -H "Authorization: Bearer your_api_key_here" \
     -X POST http://localhost:8123/tools/get_forecast \
     -H "Content-Type: application/json" \
     -d '{"latitude": 40.7128, "longitude": -74.006}'

# 获取天气警报
curl -H "Authorization: Bearer your_api_key_here" \
     -X POST http://localhost:8123/tools/get_alerts \
     -H "Content-Type: application/json" \
     -d '{"state": "NY"}'
```

## Dify 集成

### 1. 在 Dify 中配置 MCP 服务器

在 Dify 应用设置中添加 MCP 服务器配置：

```json
{
  "name": "weather-mcp",
  "url": "http://your-server:8123",
  "auth": {
    "type": "bearer",
    "token": "your_api_key_here"
  }
}
```

### 2. 工具配置

Dify 会自动发现以下工具：

- `get_forecast`: 获取指定位置的天气预报
- `get_alerts`: 获取指定州的天气警报

## 安全注意事项

1. **API Key 安全**: 不要在代码中硬编码 API Key
2. **HTTPS**: 生产环境建议使用 HTTPS
3. **防火墙**: 限制服务器访问权限
4. **监控**: 监控异常访问模式

## 故障排除

### ✅ 已解决的问题

#### MCP 连接错误 "Session terminated by server"
**原因**: FastMCP 的 `streamable_http_app` 是工厂函数，需要 `factory=True` 参数
**解决方案**: 已在代码中修复，使用 `uvicorn.run(..., factory=True)`

#### 依赖版本冲突
**原因**: FastAPI 和 MCP 对 `anyio` 版本要求不同
**解决方案**: 使用兼容的版本组合，已在 `requirements.txt` 中配置

#### 工具列表错误
**原因**: `list_tools()` 返回的是 `ListToolsResult` 对象，不是列表
**解决方案**: 使用 `tools_result.tools` 访问工具列表

### 常见问题

#### 依赖冲突

```bash
# 检查当前安装的版本
pip list | grep -E "(fastapi|httpx|mcp|anyio)"

# 解决 anyio 冲突
pip install "anyio>=4.5"
pip install -r requirements.txt
```

#### 认证失败

```bash
# 检查 API Key 是否正确设置
echo $DIFY_API_KEY

# 检查服务器日志
python weather.py --api-key test_key
```

#### 连接问题

```bash
# 检查服务器是否正在运行
curl http://localhost:8123/health

# 检查端口是否被占用
netstat -tulpn | grep 8123
```

#### 工具调用失败

```bash
# 检查工具端点
curl -H "Authorization: Bearer your_api_key_here" \
     http://localhost:8123/docs
```

## 开发模式

开发时可以使用 `--no-auth` 参数禁用认证：

```bash
python weather.py --no-auth --port 8123
```

这样可以直接测试工具功能，无需提供 API Key。

## 环境变量参考

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DIFY_API_KEY` | Dify MCP API Key | 无 |
| `MCP_API_KEY` | 备用 API Key 变量名 | 无 |
| `HOST` | 服务器绑定地址 | 0.0.0.0 |
| `PORT` | 服务器端口 | 8123 |

## 版本兼容性

| 包名 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| mcp | 1.9.0 | 最新 | MCP 核心库 |
| fastapi | 0.115.0 | 最新 | Web 框架 |
| httpx | 0.28.0 | 0.28.1 | HTTP 客户端 |
| uvicorn | 0.27.0 | 最新 | ASGI 服务器 |
| anyio | 4.5.0 | 最新 | 异步 I/O 库 |

## 验证安装

运行测试脚本验证安装：

```bash
python test_mcp_connection.py
```

成功输出应该显示：
```
✅ Connected to MCP server
✅ Session initialized
✅ Found 2 tools:
  - get_alerts: Get weather alerts for a US state.
  - get_forecast: Get weather forecast for a location.
✅ Tool call successful: [weather data]
✅ Test completed successfully
```
