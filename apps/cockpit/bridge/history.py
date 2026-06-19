"""Balance history for dashboard sparklines."""

from __future__ import annotations

import json
from pathlib import Path

HISTORY_FILE = Path.home() / ".pmxt-cockpit" / "balance-history.json"
MAX_POINTS = 48


def _load() -> dict:
    if HISTORY_FILE.is_file():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"kalshi": [], "poly": []}


def _save(data: dict) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data))


def record(kalshi: str | None, poly: str | None) -> dict[str, list[float]]:
    data = _load()
    for key, raw in (("kalshi", kalshi), ("poly", poly)):
        try:
            val = float(raw) if raw else None
        except (TypeError, ValueError):
            val = None
        if val is not None:
            series: list[float] = data.get(key, [])
            series.append(val)
            data[key] = series[-MAX_POINTS:]
    _save(data)
    return {"kalshi": data.get("kalshi", []), "poly": data.get("poly", [])}
