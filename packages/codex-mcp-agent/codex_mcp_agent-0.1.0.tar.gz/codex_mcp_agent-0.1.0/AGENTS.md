# Repository Guidelines

## Project Structure & Module Organization
- `src/codex_mcp_agent/`: Python package.
  - `server.py`: CLI entry (`codex-mcp-agent`) and mode flags.
  - `tools/`: MCP tools (`codex_execute`, `codex_review`) and registry.
  - `utils.py`: shared helpers (Codex output parsing, subprocess).
  - `prompts.py`: pre-defined review prompt templates.
  - `__main__.py`: enables `python -m codex_mcp_agent`.
- `pyproject.toml`: build (`hatchling`), runtime deps, script.
- `.mcp.json`: example local MCP client config (see README).
- `README.md`: setup, usage, and SSE/HTTP notes.

## Build, Test, and Development Commands
- Install deps (uv recommended): `uv sync` (Python 3.11+).
- Run in stdio: `uv run codex-mcp-agent --help-modes`.
- Run SSE: `uv run codex-mcp-agent --sse [--host 127.0.0.1 --port 8822]`.
- Run streamable HTTP: `uv run codex-mcp-agent --http`.
- Writable mode: add `--yolo` (e.g., `uv run codex-mcp-agent --sse --yolo`).
- Global usage from clients: `.mcp.json` can call `uvx codex-mcp-agent@latest`.

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indent, line length ~100, use type hints.
- Modules/funcs: `snake_case`; classes: `PascalCase`; constants: `UPPER_SNAKE`.
- Keep tool logic small and side‑effect free; use `ctx.log(...)` for succinct logs.
- Place shared parsing/OS calls in `utils.py`; register tools via `tools/__init__.py`.

## Testing Guidelines
- No test suite yet. If adding tests, use `pytest` with files under `tests/` named `test_*.py`.
- Prefer small, focused unit tests for `utils.py` and tool parameter validation.
- Run tests (once added): `uv run pytest -q`.

## Commit & Pull Request Guidelines
- Use Conventional Commit prefixes when possible: `feat:`, `fix:`, `refactor:`, `docs:` (e.g., `refactor(tools): split registration`).
- PRs should include: clear description, rationale, usage examples/commands, and linked issues.
- When changing behavior or flags, update `README.md` and sample `.mcp.json`.
- For riskier changes (file writes, process exec), state safety impact and how to test in SAFE vs `--yolo` mode.

## Security & Configuration Tips
- Default SAFE mode is read‑only; `--yolo` enables writes and git operations—use cautiously.
- SSE/HTTP bind to `127.0.0.1` with no auth; do not expose publicly.
- Avoid logging secrets; prefer local testing via a temporary workspace directory.

