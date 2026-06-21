"""Append-only trade audit log for live order paths."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def audit_log_paths(root: Path) -> dict[str, Path]:
    """Known append-only audit jsonl files under briefs/alerts/."""
    alerts = root / "briefs" / "alerts"
    return {
        "trades": alerts / "trades.jsonl",
        "fills": alerts / "fills.jsonl",
    }


def tail_jsonl(path: Path, *, limit: int = 50) -> list[dict[str, Any]]:
    """Return up to ``limit`` most recent JSON objects from a jsonl file."""
    if limit <= 0 or not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        text = line.strip()
        if not text:
            continue
        try:
            row = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def format_audit_entry(row: dict[str, Any]) -> str:
    """Single-line summary for cockpit / CLI display."""
    ts = row.get("timestamp") or row.get("ts") or "?"
    venue = row.get("venue") or row.get("exchange") or "?"
    cmd = row.get("command") or row.get("action") or "?"
    market = row.get("market") or row.get("marketId") or row.get("slug") or "?"
    outcome = row.get("outcome") or row.get("outcomeId") or ""
    size = row.get("size", "")
    parts = [str(ts)[:19], str(venue), str(cmd), str(market)]
    if outcome:
        parts.append(str(outcome))
    if size != "":
        parts.append(f"size={size}")
    if row.get("order_id") or row.get("orderId"):
        parts.append(f"id={row.get('order_id') or row.get('orderId')}")
    return " | ".join(parts)


def parse_order_id(stdout: str) -> str | None:
    """Best-effort order id from pmxt order:create JSON stdout."""
    text = (stdout or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(data, list) and data:
        data = data[0]
    if not isinstance(data, dict):
        return None
    for key in ("id", "orderId", "order_id"):
        val = data.get(key)
        if val:
            return str(val)
    return None


def append_trade_log(
    root: Path,
    *,
    venue: str,
    command: str,
    market: str,
    outcome: str,
    size: float | int | str,
    dry_run: bool = False,
    order_id: str | None = None,
    stdout: str | None = None,
) -> dict[str, Any]:
    """Append one JSON line to briefs/alerts/trades.jsonl (no secrets)."""
    if dry_run:
        return {}
    oid = order_id or (parse_order_id(stdout or "") if stdout else None)
    entry: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "venue": venue,
        "command": command,
        "market": market,
        "outcome": outcome,
        "size": size,
        "dry_run": False,
    }
    if oid:
        entry["order_id"] = oid
    log_path = root / "briefs" / "alerts" / "trades.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, separators=(",", ":")) + "\n")
    return entry
