"""Atomic JSON persistence with file locking and restrictive permissions."""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
from typing import Any


def read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if default is None:
        default = {}
    if not path.is_file():
        return dict(default)
    try:
        with path.open(encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
            data = json.load(handle)
        return data if isinstance(data, dict) else dict(default)
    except (json.JSONDecodeError, OSError):
        return dict(default)


def write_json(path: Path, data: dict[str, Any], *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        json.dump(data, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(tmp, mode)
    tmp.replace(path)
    os.chmod(path, mode)
