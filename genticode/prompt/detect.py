from __future__ import annotations

import ast
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


PROMPT_KEYWORDS = (
    "You are ",
    "assistant:",
    "system:",
    "user:",
    "Given the following",
    "```",
    "###",
    "LLM",
    "model",
    "prompt",
)


@dataclass(frozen=True)
class PromptSpan:
    file: Path
    start: int
    end: int
    text: str

    @property
    def id(self) -> str:
        return hashlib.sha1(self.text.encode("utf-8")).hexdigest()[:12]

    @property
    def role(self) -> str:
        t = self.text.lower()
        if "system:" in t or t.startswith("you are "):
            return "system"
        if "user:" in t:
            return "user"
        return "unknown"


def _is_prompt_like(text: str) -> bool:
    if len(text) >= 80:
        return True
    if "\n" in text:
        return True
    for kw in PROMPT_KEYWORDS:
        if kw.lower() in text.lower():
            return True
    return False


def _scan_python(path: Path) -> Iterator[PromptSpan]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return iter(())
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return iter(())

    # Walk with manual iteration to yield spans
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and _is_prompt_like(n.value):
            yield PromptSpan(path, n.lineno, getattr(n, "end_lineno", n.lineno), n.value)
        elif isinstance(n, ast.JoinedStr):
            text = "".join([s.value for s in n.values if isinstance(s, ast.Constant) and isinstance(s.value, str)])
            if _is_prompt_like(text):
                yield PromptSpan(path, n.lineno, getattr(n, "end_lineno", n.lineno), text)


_JS_STRING_RE = re.compile(r"`[^`]+`|\"[^\n\r\"]{80,}?\"|'[^\n\r']{80,}?'", re.S)


def _scan_js_ts(path: Path) -> Iterator[PromptSpan]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return iter(())
    for m in _JS_STRING_RE.finditer(src):
        s = m.group(0)
        # Strip quotes/backticks
        if s.startswith("`") and s.endswith("`"):
            txt = s[1:-1]
        elif (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            txt = s[1:-1]
        else:
            txt = s
        if _is_prompt_like(txt):
            start_line = src.count("\n", 0, m.start()) + 1
            end_line = src.count("\n", 0, m.end()) + 1
            yield PromptSpan(path, start_line, end_line, txt)


def scan_paths(paths: Iterable[Path]) -> list[PromptSpan]:
    spans: list[PromptSpan] = []
    for p in paths:
        if p.suffix == ".py":
            spans.extend(list(_scan_python(p)))
        elif p.suffix in {".js", ".ts", ".tsx", ".jsx"}:
            spans.extend(list(_scan_js_ts(p)))
    # Deterministic: sort by file, start
    spans.sort(key=lambda s: (str(s.file), s.start, s.end))
    return spans


def scan_repo(root: Path) -> list[PromptSpan]:
    candidates: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common vendor and internal dirs
        rel = os.path.relpath(dirpath, root)
        if rel.startswith(".git") or rel.startswith(".genticode") or rel.startswith(".venv") or "node_modules" in rel:
            continue
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix in {".py", ".js", ".ts", ".tsx", ".jsx"}:
                candidates.append(p)
    return scan_paths(candidates)
