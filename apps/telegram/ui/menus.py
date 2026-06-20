"""Menu tree from ui-spec.json."""

from __future__ import annotations

from typing import Any

from apps.telegram.ui.loader import load_ui_spec

MAIN_MENU_ID = "main"


def menu_title(menu_id: str) -> str:
    spec = load_ui_spec()
    if menu_id == MAIN_MENU_ID:
        return spec["mainMenu"]["title"]
    sub = spec.get("subMenus", {}).get(menu_id)
    if sub:
        return sub["title"]
    return menu_id


def menu_items(menu_id: str = MAIN_MENU_ID) -> list[dict[str, Any]]:
    spec = load_ui_spec()
    if menu_id == MAIN_MENU_ID:
        return list(spec["mainMenu"]["items"])
    sub = spec.get("subMenus", {}).get(menu_id)
    if sub:
        return list(sub["items"])
    return list(spec["mainMenu"]["items"])


def submenu_ids() -> list[str]:
    return list(load_ui_spec().get("subMenus", {}).keys())
