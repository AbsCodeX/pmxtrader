"""Parse ./pmx status and related output."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


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


# Balance blocks start at column 0 ("Kalshi:" / "Polymarket US:"). Panic-scope lines are
# indented ("  Kalshi: included") and must not be matched — otherwise Poly picks Kalshi cash.
_KALSHI_BAL_RE = re.compile(
    r"^Kalshi:\s*\n\s*available:\s*([\d.]+)(?:\s+total:\s*([\d.]+))?",
    re.M,
)
_POLY_BAL_RE = re.compile(
    r"^Polymarket US:\s*\n\s*available:\s*([\d.]+)(?:\s+total:\s*([\d.]+))?",
    re.M,
)


def _fmt_money(value: object) -> str | None:
    if value is None:
        return None
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def parse_balance_json(stdout: str) -> tuple[str | None, str | None]:
    """Parse pmxt balance --json output (Kalshi raw JSON or Poly US with header lines)."""
    if not stdout.strip():
        return None, None
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped.startswith("["):
            continue
        try:
            rows = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            row = rows[0]
            return _fmt_money(row.get("available")), _fmt_money(row.get("total"))
    try:
        rows = json.loads(stdout.strip())
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            row = rows[0]
            return _fmt_money(row.get("available")), _fmt_money(row.get("total"))
    except json.JSONDecodeError:
        pass
    return None, None


def parse_status(stdout: str) -> StatusSummary:
    s = StatusSummary()
    s.kill_switch = parse_kill_switch(stdout)
    m = _KALSHI_BAL_RE.search(stdout)
    if m:
        s.kalshi_available = m.group(1)
        s.kalshi_total = m.group(2)
    m = _POLY_BAL_RE.search(stdout)
    if m:
        s.poly_available = m.group(1)
        s.poly_total = m.group(2)
    return s


_QUOTE_PATTERNS: dict[str, re.Pattern[str]] = {
    "best_bid": re.compile(r"Best bid:\s*([\d.]+)", re.I),
    "best_ask": re.compile(r"Best ask:\s*([\d.]+)", re.I),
    "mid": re.compile(r"Mid:\s*([\d.]+)", re.I),
    "last": re.compile(r"(?:Last|Price):\s*([\d.]+)", re.I),
    "fill_est": re.compile(r"Fill est(?:\.|:)?\s*.*?([\d.]+)", re.I),
    "event_id": re.compile(r"Event:\s*(\S+)", re.I),
    "market_id": re.compile(r"Market:\s*(\S+)", re.I),
    "slug": re.compile(r"Slug:\s*(\S+)", re.I),
    "outcome": re.compile(r"Outcome:\s*(.+)", re.I),
}

_RULES_PATTERNS = (
    re.compile(r"^Resolution:\s*(.+)$", re.I | re.M),
    re.compile(r"^Rules:\s*(.+)$", re.I | re.M),
    re.compile(r"^Description:\s*(.+)$", re.I | re.M),
)


def parse_quote_fields(stdout: str) -> dict[str, str | float]:
    """Extract structured quote/book fields from link/quote stdout."""
    out: dict[str, str | float] = {}
    for key, pat in _QUOTE_PATTERNS.items():
        m = pat.search(stdout)
        if not m:
            continue
        raw = m.group(1).strip()
        if key in ("event_id", "market_id", "slug", "outcome"):
            out[key] = raw
        else:
            try:
                out[key] = float(raw)
            except ValueError:
                out[key] = raw
    return out


def parse_rules_note(stdout: str) -> dict[str, str]:
    """Best-effort rules/resolution snippet from analyzer output."""
    chunks: list[str] = []
    for pat in _RULES_PATTERNS:
        m = pat.search(stdout)
        if m:
            chunks.append(m.group(1).strip())
    text = " | ".join(chunks) if chunks else ""
    return {
        "text": text,
        "manual_required": not bool(text),
        "hint": "Copy full resolution criteria from Kalshi/Poly market page into brief",
    }


def parse_positions_json(stdout: str) -> list[dict[str, Any]]:
    """Parse JSON position arrays from ./pmx positions / poly positions."""
    if not stdout.strip():
        return []
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") or stripped.startswith("{"):
            try:
                data = json.loads(stripped if stripped.startswith("[") else stdout.strip())
            except json.JSONDecodeError:
                continue
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
            if isinstance(data, dict):
                for key in ("positions", "data", "results"):
                    inner = data.get(key)
                    if isinstance(inner, list):
                        return [x for x in inner if isinstance(x, dict)]
    try:
        data = json.loads(stdout.strip())
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
    except json.JSONDecodeError:
        pass
    return []
