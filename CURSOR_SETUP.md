# Cursor MCP 服务器配置指南

## 概述

本指南将帮助你在 Cursor 中配置 MCP (Model Context Protocol) 服务器，以便远程访问天气查询工具。

## 方法一：HTTP 传输方式（推荐）

### 1. 启动 MCP 服务器

```bash
cd server
python weather.py --port 8123
```

### 2. 配置 Cursor

在 Cursor 中打开设置（Settings），找到 MCP 配置部分，添加以下配置：

#### 方法 A：通过 Cursor 设置界面
1. 打开 Cursor
2. 按 `Cmd/Ctrl + ,` 打开设置
3. 搜索 "MCP" 或 "Model Context Protocol"
4. 添加新的 MCP 服务器配置

#### 方法 B：直接编辑配置文件
在 Cursor 的配置文件中添加：

```json
{
  "mcpServers": {
    "weather-server": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8123/mcp"
      }
    }
  }
}
```

### 3. 验证连接

重启 Cursor 后，你应该能够：
- 在聊天中看到可用的天气工具
- 使用 `get_alerts` 和 `get_forecast` 工具

## 方法二：stdio 传输方式

### 1. 配置 Cursor

```json
{
  "mcpServers": {
    "weather-server": {
      "command": "python",
      "args": ["weather.py", "--port", "8123"],
      "cwd": "/path/to/your/project/server",
      "env": {},
      "transport": {
        "type": "stdio"
      }
    }
  }
}
```

## 可用的工具

### 1. get_alerts
获取美国各州的天气警报
- **参数**: `state` (两字母州代码，如 CA, NY)
- **示例**: "Get weather alerts for California"

### 2. get_forecast
根据经纬度获取天气预报
- **参数**: 
  - `latitude` (纬度)
  - `longitude` (经度)
- **示例**: "Get weather forecast for New York City (40.7128, -74.0060)"

### 3. get_tool_test
测试工具连接
- **参数**: `query` (任意字符串)
- **示例**: "Test the MCP connection"

## 故障排除

### 1. 服务器无法启动
- 检查端口 8123 是否被占用
- 确保所有依赖已安装：`pip install -e .`

### 2. Cursor 无法连接
- 确认服务器正在运行：`curl http://localhost:8123/health`
- 检查防火墙设置
- 重启 Cursor

### 3. 工具不可用
- 检查 MCP 配置是否正确
- 查看 Cursor 的开发者工具中的错误信息
- 确认服务器日志中是否有错误

## 高级配置

### 自定义端口
如果 8123 端口被占用，可以使用其他端口：

```bash
python weather.py --port 8124
```

然后更新 Cursor 配置中的 URL：
```json
{
  "transport": {
    "type": "http",
    "url": "http://localhost:8124/mcp"
  }
}
```

### 远程访问
要让其他机器访问，需要修改服务器启动参数：

```bash
python weather.py --port 8123 --host 0.0.0.0
```

然后使用服务器的 IP 地址：
```json
{
  "transport": {
    "type": "http",
    "url": "http://YOUR_SERVER_IP:8123/mcp"
  }
}
```

## 使用示例

在 Cursor 聊天中，你可以这样使用：

```
用户: What's the weather like in San Francisco?
助手: I'll check the weather forecast for San Francisco. Let me get the coordinates and fetch the forecast.

[使用 get_forecast 工具获取旧金山的天气预报]

用户: Are there any weather alerts in Texas?
助手: I'll check for any active weather alerts in Texas.

[使用 get_alerts 工具获取德克萨斯州的天气警报]
```

## 注意事项

1. **安全性**: 当前配置仅适用于本地开发，生产环境需要适当的安全措施
2. **性能**: 天气 API 调用可能需要几秒钟时间
3. **限制**: NWS API 有使用限制，请合理使用
4. **错误处理**: 如果 API 不可用，工具会返回错误信息 