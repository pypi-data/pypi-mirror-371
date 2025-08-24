"""codex_research tool definition.

Generates an initial investigation/analysis report for a given topic in the codebase.
"""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from ..utils import run_and_extract_codex_blocks


def register(mcp: FastMCP, *, safe_mode: bool) -> None:
    @mcp.tool()
    async def codex_research(
        system_prompt: str,
        work_dir: str,
        topic: str,
        ctx: Context | None = None,
    ) -> str:
        """Produce an analysis report around a topic using the repository code.

        Args:
            system_prompt: High-level system guidance for the research process.
            work_dir: Repository/workspace directory to analyze.
            topic: Investigation topic or question to answer.
        """

        if ctx is not None and hasattr(ctx, "log"):
            try:
                ctx.log(f"codex_research: work_dir={work_dir}, topic={topic[:80]}")
            except Exception:
                pass

        safety_hint = (
            "You are operating in a read-only sandbox. Do not modify files; prefer listing and reading files only."
            if safe_mode
            else "You may modify files if strictly necessary, but prefer analysis without writes."
        )

        final_prompt = f"""
{system_prompt}

Context:
- Work directory: {work_dir}
- Safety: {safety_hint}

Goal:
Investigate the following topic within this repository and produce a concise, actionable analysis:
"{topic}"

Process Guidelines:
1) Map the project layout (key packages, entrypoints, tools, configs).
2) Identify modules, functions, or data relevant to the topic.
3) Read only the necessary files; quote key snippets with file paths and line ranges.
4) Note behaviors, assumptions, and risks; highlight missing pieces or unknowns.
5) Propose next steps (experiments, code changes, tests, or metrics) with commands.

Deliverable (use this structure):
- Summary: 3–6 bullet points.
- Key Areas: modules/files and their roles (with paths).
- Findings: evidence-backed observations with inline quotes.
- Risks & Gaps: potential issues and open questions.
- Next Steps: prioritized actions with concrete commands.
"""

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
                ctx.log("codex_research: done")
            except Exception:
                pass
        return result

