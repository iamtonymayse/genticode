from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Fix:
    description: str
    patched: str


def _mk_const_name(sid: str) -> str:
    return f"PROMPT_{sid.upper()}"


def suggest_autofix(lang: str, content: str, literal: str, sid: str) -> Fix:
    """Return a patched file content extracting the given literal to a const.

    - lang: "py" or "ts"/"js"
    - literal: the string literal content (without quotes)
    """
    const_name = _mk_const_name(sid)
    if lang == "py":
        header = f"{const_name} = \"\"\"{literal}\"\"\"\n\n"
        # Replace first occurrence of the string literal with the const name
        # Try triple-quoted first
        patched = content
        if literal in patched:
            # Replace quoted forms conservatively
            patched = patched.replace(f'"""{literal}"""', const_name, 1)
            patched = patched.replace(f"'''{literal}'''", const_name, 1)
            patched = patched.replace(f'"{literal}"', const_name, 1)
            patched = patched.replace(f"'{literal}'", const_name, 1)
        return Fix("extract to module-level constant", header + patched)
    else:
        # JS/TS: use const with backticks
        header = f"const {const_name} = `{literal}`;\n\n"
        patched = content
        # Replace template/backtick form first, then quotes
        patched = patched.replace(f"`{literal}`", const_name, 1)
        patched = patched.replace(f'"{literal}"', const_name, 1)
        patched = patched.replace(f"'{literal}'", const_name, 1)
        return Fix("extract to top-level const", header + patched)

