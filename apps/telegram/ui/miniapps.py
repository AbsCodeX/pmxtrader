"""Mini App URLs from env — mirrors telegram/miniapps.ts."""

from __future__ import annotations

import os
from dataclasses import dataclass

from apps.telegram.ui.loader import load_ui_spec


@dataclass(frozen=True)
class MiniAppUrls:
    dashboard: str
    terminal: str
    portfolio: str
    research: str
    agents: str
    settings: str


def load_mini_app_urls() -> MiniAppUrls:
    spec = load_ui_spec()["miniApps"]
    env_keys: dict[str, str] = spec["envKeys"]
    defaults: dict[str, str] = spec["defaults"]
    values = {
        key: os.environ.get(env_keys[key], "").strip() or defaults[key]
        for key in env_keys
    }
    return MiniAppUrls(**values)


def mini_app_labels() -> dict[str, str]:
    return dict(load_ui_spec()["miniApps"]["labels"])
