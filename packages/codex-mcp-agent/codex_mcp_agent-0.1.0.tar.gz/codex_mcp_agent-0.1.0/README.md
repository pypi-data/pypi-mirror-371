# codex-mcp-agent

[中文版](./README.zh-CN.md)

Note: This project is a fork of the current Git remote:

- origin: https://github.com/1WorldCapture/codex-as-mcp

Enable Claude Code, Cursor and other AI tools to call Codex for task execution. Plus/Pro/Team subscribers can maximize GPT-5 usage without additional costs.

## Setup

### 1. Install Codex CLI
```bash
npm install -g @openai/codex
codex login
```

### 2. Configure MCP

Add to your `.mcp.json`:
**Safe Mode (Default):**
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

**Writable Mode:**
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

Or use Claude Code commands:
```bash
# Safe mode (default)
claude mcp add codex-mcp-agent -- uvx codex-mcp-agent@latest

# Writable mode
claude mcp add codex-mcp-agent -- uvx codex-mcp-agent@latest --yolo
```

## Tools

The MCP server exposes two tools:
- `codex_execute(prompt, work_dir)` - General purpose codex execution
- `codex_review(review_type, work_dir, target?, prompt?)` - Specialized code review

If you have any other use case requirements, feel free to open issue.

## HTTP/SSE Mode (Optional)

For local personal use, you can run the server over HTTP with Server-Sent Events (SSE) and connect via `type: "sse"`.

Start the server in SSE mode:
```bash
uvx codex-mcp-agent@latest --sse            # safe mode, localhost:8822
uvx codex-mcp-agent@latest --sse --yolo     # writable mode

# Options
#   --host  (default: 127.0.0.1)
#   --port  (default: 8822)
```

Configure your client `.mcp.json`:
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

Notes:
- SSE mode keeps the same Safe/Writable behavior controlled by `--yolo`.
- SSE server binds to `127.0.0.1` by default and has no auth/CORS for simplicity.
- Stdio mode remains the default; use `--sse` only if you prefer HTTP.

Optional: Streamable HTTP transport (if your client supports it):
```bash
uvx codex-mcp-agent@latest --http           # safe mode streamable-http transport
```

## Safety

- **Safe Mode**: Default read-only operations protect your environment
- **Writable Mode**: Use `--yolo` flag when you need full codex capabilities
- **Sequential Execution**: Prevents conflicts from parallel agent operations
