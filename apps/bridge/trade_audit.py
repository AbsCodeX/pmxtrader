"""Append-only trade audit log for live order paths."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


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
