"""codex_review tool definition."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from ..utils import run_and_extract_codex_blocks


def register(mcp: FastMCP, *, safe_mode: bool, review_prompts: dict[str, str]) -> None:
    @mcp.tool()
    async def codex_review(
        review_type: str,
        work_dir: str,
        target: str = "",
        prompt: str = "",
        ctx: Context | None = None,
    ) -> str:
        """Execute code review using codex with pre-defined review prompts."""
        if review_type not in review_prompts:
            raise ValueError(f"Invalid review_type '{review_type}'. Must be one of: {list(review_prompts.keys())}")

        template = review_prompts[review_type]
        custom_prompt_section = f"\nAdditional instructions: {prompt}" if prompt else ""
        final_prompt = template.format(
            target=target if target else "current scope",
            custom_prompt=custom_prompt_section,
        )

        if ctx is not None and hasattr(ctx, "log"):
            try:
                ctx.log(f"codex_review: type={review_type}, work_dir={work_dir}, target={target}")
            except Exception:
                pass

        cmd = [
            "codex",
            "exec",
            "--full-auto",
            "--skip-git-repo-check",
            "--cd",
            work_dir,
            final_prompt,
        ]
        result = run_and_extract_codex_blocks(cmd, safe_mode=safe_mode)[-1]["raw"]
        if ctx is not None and hasattr(ctx, "log"):
            try:
                ctx.log("codex_review: done")
            except Exception:
                pass
        return result

