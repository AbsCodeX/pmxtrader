"""Load shared UI spec from telegram-ui/ui-spec.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def spec_path() -> Path:
    return repo_root() / "telegram-ui" / "ui-spec.json"


@lru_cache(maxsize=1)
def load_ui_spec() -> dict[str, Any]:
    path = spec_path()
    if not path.is_file():
        raise FileNotFoundError(f"Telegram UI spec missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
