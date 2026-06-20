"""Balance history for dashboard sparklines."""

from __future__ import annotations

from pathlib import Path

from apps.cockpit.bridge.json_store import read_json, write_json

HISTORY_FILE = Path.home() / ".pmxt-cockpit" / "balance-history.json"
MAX_POINTS = 48


def _load() -> dict:
    return read_json(HISTORY_FILE, {"kalshi": [], "poly": []})


def _save(data: dict) -> None:
    write_json(HISTORY_FILE, data)


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
