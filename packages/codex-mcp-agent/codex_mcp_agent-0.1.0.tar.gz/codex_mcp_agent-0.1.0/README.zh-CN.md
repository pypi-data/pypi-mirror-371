# codex-mcp-agent

让 Claude Code、Cursor 等 AI 工具调用 Codex 执行任务。Plus/Pro/Team 订阅用户可在不增加额外费用的情况下最大化使用 GPT-5。

注：本项目来自当前 Git 远程仓库的 fork：

- origin: https://github.com/1WorldCapture/codex-as-mcp

## 安装与配置

### 1. 安装 Codex CLI
```bash
npm install -g @openai/codex
codex login
```

### 2. 配置 MCP

在 `.mcp.json` 中添加：
【安全模式（默认）】
```json
{
  "mcpServers": {
    "codex": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-mcp-agent@latest"]
    }
  }
}
```

【可写模式】
```json
{
  "mcpServers": {
    "codex": {
      "type": "stdio",
      "command": "uvx",
      "args": ["codex-mcp-agent@latest", "--yolo"]
    }
  }
}
```

或者使用 Claude Code 命令：
```bash
# 安全模式（默认）
claude mcp add codex-mcp-agent -- uvx codex-mcp-agent@latest

# 可写模式
claude mcp add codex-mcp-agent -- uvx codex-mcp-agent@latest --yolo
```

## 工具

MCP 服务器暴露两个工具：
- `codex_execute(prompt, work_dir)`：通用的 Codex 执行
- `codex_review(review_type, work_dir, target?, prompt?)`：专项代码审查

如有其他使用场景需求，欢迎提交 issue。

## HTTP/SSE 模式（可选）

若你更喜欢通过本地 HTTP + SSE 连接（个人使用），可以以 SSE 模式运行服务并在客户端使用 `type: "sse"` 连接。

以 SSE 模式启动：
```bash
uvx codex-mcp-agent@latest --sse            # 安全模式，监听 127.0.0.1:8822
uvx codex-mcp-agent@latest --sse --yolo     # 可写模式

# 可选参数
#   --host  （默认：127.0.0.1）
#   --port  （默认：8822）
```

在客户端 `.mcp.json` 中配置：
```json
{
  "mcpServers": {
    "codex": {
      "type": "sse",
      "url": "http://127.0.0.1:8822"
    }
  }
}
```

说明：
- SSE 模式下 `--yolo` 的安全/可写行为与 stdio 一致。
- 为简化个人使用，SSE 服务默认仅绑定 `127.0.0.1`，不启用鉴权/CORS。
- 默认仍是 stdio 模式；只有在需要 HTTP 时才加 `--sse`。

可选：若客户端支持 streamable-http 传输，可使用：
```bash
uvx codex-mcp-agent@latest --http           # 启动 streamable-http 传输
```

## 安全性

- 安全模式：默认只读操作，保护你的环境
- 可写模式：需要完整能力时使用 `--yolo` 标志
- 顺序执行：避免多代理并行操作产生冲突
