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
