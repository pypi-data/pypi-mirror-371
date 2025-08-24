"""Shared utilities for tools.

- Regex and parser to extract Codex output blocks
"""

from __future__ import annotations

import re
import subprocess
from typing import Dict, List, Optional, Sequence

# Regex patterns to parse blocks in Codex output
HEADER_RE = re.compile(
    r"^"
    r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\]"  # timestamp
    r"\s+"
    r"([^\n]+)"  # tag
    r"\n",
    flags=re.M,
)

BLOCK_RE = re.compile(
    r"^"
    r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\]\s+([^\n]+)\n"  # ts, tag
    r"(.*?)"  # body
    r"(?=^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\]\s+[^\n]+\n|\Z)",
    flags=re.M | re.S,
)


def run_and_extract_codex_blocks(
    cmd: Sequence[str],
    tags: Optional[Sequence[str]] = ("codex",),
    last_n: int = 1,
    safe_mode: bool = True,
) -> List[Dict[str, str]]:
    """Run a command and extract the last N timestamped log blocks.

    A block is defined as:
        [YYYY-MM-DDTHH:MM:SS] <tag>\n
        <body until next header or EOF>

    Returns blocks in chronological order.
    """
    # Adjust command for safe mode
    final_cmd = list(cmd)
    if safe_mode:
        if "--full-auto" in final_cmd:
            idx = final_cmd.index("--full-auto")
            final_cmd[idx : idx + 1] = ["--sandbox", "read-only"]

    proc = subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = proc.stdout

    blocks: List[Dict[str, str]] = []
    allowed = {t.lower() for t in tags} if tags is not None else None
    for m in BLOCK_RE.finditer(out):
        ts, tag, body = m.group(1), m.group(2).strip(), m.group(3)
        if allowed is None or tag.lower() in allowed:
            raw = f"[{ts}] {tag}\n{body}"
            blocks.append({"timestamp": ts, "tag": tag, "body": body, "raw": raw})

    return blocks[-last_n:]

