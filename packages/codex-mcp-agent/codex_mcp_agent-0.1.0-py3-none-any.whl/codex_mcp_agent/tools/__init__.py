"""Tool registration entrypoint.

Unifies registration so each tool can declare only what it needs.
Adds per-tool context (e.g., safe_mode) via ToolSpec while keeping
server compatibility.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Import tool modules (module-level import keeps order explicit and stable)
from . import codex_execute as _mod_codex_execute
from . import codex_review as _mod_codex_review
from . import codex_research as _mod_codex_research


@dataclass
class ToolSpec:
    module: Any
    name: str = ""
    enabled: bool = True
    ctx: Dict[str, Any] = field(default_factory=dict)


def _resolve_safe_mode(value: Any, default: bool) -> bool:
    """Resolve per-tool safe_mode with support for 'inherit'."""
    if value is None or value == "inherit":
        return default
    if isinstance(value, bool):
        return value
    # Fallback: try to parse truthy strings; otherwise use default
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "true", "yes", "on"}:
            return True
        if v in {"0", "false", "no", "off"}:
            return False
    return default


# Explicit tool specs. review_prompts is injected at runtime in register_tools.
MODULE_SPECS: List[ToolSpec] = [
    ToolSpec(module=_mod_codex_execute, name="codex_execute", ctx={"safe_mode": "inherit"}),
    ToolSpec(module=_mod_codex_review, name="codex_review", ctx={"safe_mode": "inherit"}),
    ToolSpec(module=_mod_codex_research, name="codex_research", ctx={"safe_mode": "inherit"}),
]


def _filtered_kwargs(func: Callable[..., Any], candidates: dict[str, Any]) -> dict[str, Any]:
    """Return only kwargs that `func` accepts (by parameter name)."""
    try:
        sig = inspect.signature(func)
        allowed = {name for name, p in sig.parameters.items() if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)}
        return {k: v for k, v in candidates.items() if k in allowed}
    except (TypeError, ValueError):  # builtins or C funcs without signatures
        return {}


def register_tools(mcp: FastMCP, *, safe_mode: bool, review_prompts: dict[str, str]) -> None:
    """Register all tools on the given FastMCP instance.

    Tools define a `register(mcp, ..., *)` function. This registry passes a
    per-tool context and filters kwargs so each tool only receives what it needs.

    Compatibility: `review_prompts` is injected only for the review tool.
    """
    default_ctx: Dict[str, Any] = {"safe_mode": safe_mode}

    for spec in MODULE_SPECS:
        if not spec.enabled:
            continue
        mod = spec.module
        register = getattr(mod, "register", None)
        if register is None:
            continue

        # Merge contexts: per-tool overrides > defaults
        merged: Dict[str, Any] = {**default_ctx, **(spec.ctx or {})}

        # Back-compat: only the review tool receives review_prompts
        if mod is _mod_codex_review and "review_prompts" not in merged:
            merged["review_prompts"] = review_prompts

        # Resolve per-tool safe_mode (supports 'inherit')
        merged["safe_mode"] = _resolve_safe_mode(merged.get("safe_mode"), default_ctx["safe_mode"])

        kwargs = _filtered_kwargs(register, merged)
        try:
            register(mcp, **kwargs)
        except Exception as exc:
            # Log and continue with other tools
            name = spec.name or getattr(mod, "__name__", str(mod))
            print(f"[tools] Failed to register {name}: {exc}")
