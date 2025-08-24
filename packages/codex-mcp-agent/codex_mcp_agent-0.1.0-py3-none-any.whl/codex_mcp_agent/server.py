from mcp.server.fastmcp import FastMCP, Context
import argparse
import sys
from typing import List, Dict, Optional, Sequence

SAFE_MODE = True  # default; may be toggled via --yolo

mcp = FastMCP("codex-mcp-agent")


def run_sse_server(host: str, port: int) -> None:
    """Start SSE server using FastMCP's built-in transport."""
    # Update host/port in settings then run with SSE transport
    mcp.settings.host = host
    mcp.settings.port = port
    mcp.run(transport="sse")


from .prompts import REVIEW_PROMPTS
from .tools import register_tools


"""Tools and prompts are now defined in separate modules and registered at runtime."""


def main():
    """Entry point for the MCP server"""
    global SAFE_MODE
    
    parser = argparse.ArgumentParser(
        prog="codex-mcp-agent",
        description="MCP server that provides codex agent tools"
    )
    parser.add_argument(
        "--yolo", 
        action="store_true",
        help="Enable writable mode (allows file modifications, git operations, etc.)"
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Run an HTTP/SSE server (localhost only by default)"
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the Streamable HTTP transport (localhost only by default)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind for SSE mode (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8822,
        help="Port to listen on for SSE mode (default: 8822)"
    )
    parser.add_argument(
        "--help-modes",
        action="store_true", 
        help="Show detailed explanation of safe vs writable modes"
    )
    
    args = parser.parse_args()
    
    if args.help_modes:
        print("""
codex-mcp-agent Execution Modes:

🔒 Safe Mode (default):
  - Read-only operations only
  - No file modifications
  - No git operations  
  - Safe for exploration and analysis
  
⚡ Writable Mode (--yolo):
  - Full codex agent capabilities
  - Can modify files, run git commands
  - Sequential execution prevents conflicts
  - Use with caution in production
  
Why Sequential Execution?
Codex is an agent that modifies files and system state. Running multiple
instances in parallel could cause file conflicts, git race conditions,
and conflicting system modifications. Sequential execution is safer.
""")
        sys.exit(0)
    
    # Set safe mode based on --yolo flag
    SAFE_MODE = not args.yolo
    
    if SAFE_MODE:
        print("🔒 Running in SAFE mode (read-only). Use --yolo for writable mode.")
    else:
        print("⚡ Running in WRITABLE mode. Codex can modify files and system state.")

    # Register tools with current safety mode and prompts
    register_tools(mcp, safe_mode=SAFE_MODE, review_prompts=REVIEW_PROMPTS)

    if args.sse:
        print(f"📡 SSE server listening on http://{args.host}:{args.port}")
        print("   Configure your client with type=\"sse\" and the URL above.")
        run_sse_server(args.host, args.port)
    elif args.http:
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        print(f"🌐 Streamable HTTP listening on http://{args.host}:{args.port}")
        print("   Client must support MCP streamable-http transport.")
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
