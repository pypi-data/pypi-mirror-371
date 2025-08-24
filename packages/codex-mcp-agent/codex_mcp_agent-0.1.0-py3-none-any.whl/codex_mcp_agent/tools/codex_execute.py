"""codex_execute tool definition."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from ..utils import run_and_extract_codex_blocks


def register(mcp: FastMCP, *, safe_mode: bool) -> None:
    @mcp.tool()
    async def codex_execute(prompt: str, work_dir: str, ctx: Context) -> str:
        """Execute prompt using codex for general purpose."""
        if hasattr(ctx, "log"):
            try:
                ctx.log(f"codex_execute: work_dir={work_dir}")
            except Exception:
                pass

        cmd = [
            "codex",
            "exec",
            "--full-auto",
            "--skip-git-repo-check",
            "--cd",
            work_dir,
            prompt,
        ]
        result = run_and_extract_codex_blocks(cmd, safe_mode=safe_mode)[-1]["raw"]
        if hasattr(ctx, "log"):
            try:
                ctx.log("codex_execute: done")
            except Exception:
                pass
        return result

