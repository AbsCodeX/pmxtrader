"""Robust .env parsing (multiline quoted values, escaped newlines)."""

from __future__ import annotations

from pathlib import Path


def parse_dotenv(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    lines = text.splitlines(keepends=True)
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        trimmed = line.strip()
        idx += 1
        if not trimmed or trimmed.startswith("#") or "=" not in trimmed:
            continue
        key, val = trimmed.split("=", 1)
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and not val.endswith('"'):
            buf = [val[1:]]
            while idx < len(lines):
                part = lines[idx].rstrip("\n")
                idx += 1
                if part.endswith('"'):
                    buf.append(part[:-1])
                    break
                buf.append(part)
            val = "\n".join(buf)
        elif val.startswith("'") and not val.endswith("'"):
            buf = [val[1:]]
            while idx < len(lines):
                part = lines[idx].rstrip("\n")
                idx += 1
                if part.endswith("'"):
                    buf.append(part[:-1])
                    break
                buf.append(part)
            val = "\n".join(buf)
        else:
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            val = val.replace("\\n", "\n")
        if key:
            pairs[key] = val
    return pairs


def load_dotenv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return parse_dotenv(path.read_text(encoding="utf-8"))
