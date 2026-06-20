"""Brief approval helpers for Telegram handoff."""

from __future__ import annotations

import re
from pathlib import Path

from apps.telegram.config import TelegramConfig


def list_active_briefs(cfg: TelegramConfig) -> list[Path]:
    active = cfg.root / "briefs" / "active"
    if not active.is_dir():
        return []
    return sorted(active.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)


def brief_is_approved(path: Path) -> bool:
    try:
        head = path.read_text(encoding="utf-8").split("---", 2)
    except OSError:
        return False
    if len(head) < 2:
        return False
    return bool(re.search(r"^approved:\s*true\s*$", head[1], re.M | re.I))


def approve_brief(path: Path) -> tuple[bool, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, str(exc)
    if not text.startswith("---"):
        return False, "Brief missing YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter"
    front = parts[1]
    if re.search(r"^approved:\s*true\s*$", front, re.M | re.I):
        return True, "Already approved"
    if re.search(r"^approved:\s*false\s*$", front, re.M | re.I):
        front = re.sub(r"^approved:\s*false\s*$", "approved: true", front, count=1, flags=re.M | re.I)
    else:
        front = front.rstrip() + "\napproved: true\n"
    new_text = f"---{front}---{parts[2]}"
    path.write_text(new_text, encoding="utf-8")
    return True, "Brief approved"


def brief_summary(path: Path, *, max_chars: int = 500) -> str:
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return path.name
    title = path.stem
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    approved = "approved" if brief_is_approved(path) else "pending"
    snippet = body[:max_chars].strip()
    return f"{title}\n({approved}) — {path.name}\n\n{snippet}…"
