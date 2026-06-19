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


def parse_status(stdout: str) -> StatusSummary:
    s = StatusSummary()
    s.kill_switch = re.search(r"^(ON|OFF)", stdout, re.M).group(1) if re.search(r"^(ON|OFF)", stdout, re.M) else "?"
    m = re.search(r"Kalshi:[\s\S]*?available:\s*([\d.]+)(?:\s+total:\s*([\d.]+))?", stdout)
    if m:
        s.kalshi_available = m.group(1)
        s.kalshi_total = m.group(2)
    m = re.search(r"Polymarket US:[\s\S]*?available:\s*([\d.]+)(?:\s+total:\s*([\d.]+))?", stdout)
    if m:
        s.poly_available = m.group(1)
        s.poly_total = m.group(2)
    return s
