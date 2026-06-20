"""Parse ./pmx status and related output."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class StatusSummary:
    kill_switch: str = "?"
    kalshi_available: str | None = None
    kalshi_total: str | None = None
    poly_available: str | None = None
    poly_total: str | None = None


def parse_kill_switch(stdout: str) -> str:
    """Map kill-switch status line to ON / OFF / ?."""
    if re.search(r"^ENGAGED\b", stdout, re.M):
        return "ON"
    if re.search(r"^OFF\b", stdout, re.M):
        return "OFF"
    m = re.search(r"^(ON|OFF)\b", stdout, re.M)
    if m:
        return m.group(1)
    if re.search(r"Kill switch ON", stdout, re.I):
        return "ON"
    return "?"


_PREVIEW_LINE_PREFIXES = (
    "Event:",
    "Outcome:",
    "Market:",
    "Slug:",
    "Price:",
    "Fill est:",
    "Fill:",
    "Book:",
    "Side:",
    "Size:",
    "Cost:",
    "Total:",
    "Estimated",
    "Best bid:",
    "Best ask:",
    "Mid:",
)


def extract_trade_preview(stdout: str, *, max_lines: int = 12) -> str:
    """Pull human-readable quote/fill lines from link-analyzer stdout."""
    if not stdout:
        return ""
    picked: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if lower.startswith(("error:", "failed", "warning:", "unavailable")):
            picked.append(stripped)
            continue
        if any(stripped.startswith(prefix) for prefix in _PREVIEW_LINE_PREFIXES):
            picked.append(stripped)
        if len(picked) >= max_lines:
            break
    return "\n".join(picked)


def parse_status(stdout: str) -> StatusSummary:
    s = StatusSummary()
    s.kill_switch = parse_kill_switch(stdout)
    m = re.search(r"Kalshi:[\s\S]*?available:\s*([\d.]+)(?:\s+total:\s*([\d.]+))?", stdout)
    if m:
        s.kalshi_available = m.group(1)
        s.kalshi_total = m.group(2)
    m = re.search(r"Polymarket US:[\s\S]*?available:\s*([\d.]+)(?:\s+total:\s*([\d.]+))?", stdout)
    if m:
        s.poly_available = m.group(1)
        s.poly_total = m.group(2)
    return s
