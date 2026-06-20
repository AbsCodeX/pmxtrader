"""Callback naming — mirrors telegram/callbacks.ts."""

from __future__ import annotations

from dataclasses import dataclass

CALLBACK_PREFIX = "pmx:"
LEGACY_PREFIXES = ("act:", "trade:", "brief:", "link:", "queue:", "mode:")


@dataclass(frozen=True)
class ParsedCallback:
    raw: str
    prefix: str
    action: str
    parts: tuple[str, ...]


def build_callback(action: str, *parts: str) -> str:
    body = ":".join([action, *parts]) if parts else action
    data = f"{CALLBACK_PREFIX}{body}"
    if len(data) > 64:
        raise ValueError(f"callback_data too long ({len(data)}): {data}")
    return data


def parse_callback(data: str) -> ParsedCallback:
    if data.startswith(CALLBACK_PREFIX):
        rest = data[len(CALLBACK_PREFIX) :]
        parts = tuple(rest.split(":")) if rest else ()
        action = parts[0] if parts else ""
        return ParsedCallback(raw=data, prefix=CALLBACK_PREFIX, action=action, parts=parts[1:])
    legacy = next((p for p in LEGACY_PREFIXES if data.startswith(p)), "")
    action = legacy.replace(":", "") if legacy else "unknown"
    return ParsedCallback(raw=data, prefix=legacy, action=action, parts=tuple(data.split(":")[1:]))
