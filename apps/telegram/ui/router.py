"""Route pmx: callbacks to actions for apps/telegram/bot.py."""

from __future__ import annotations

from dataclasses import dataclass

from apps.telegram.ui.callbacks import parse_callback
from apps.telegram.ui.loader import load_ui_spec
from apps.telegram.ui.menus import MAIN_MENU_ID, submenu_ids


@dataclass(frozen=True)
class UiRoute:
    kind: str
    menu_id: str = MAIN_MENU_ID
    sub_action: str = ""
    page: int = 0
    token: str = ""
    prompt: str = ""
    requires_hermes: bool = False
    requires_admin: bool = False
    blocked_in_group: bool = False


def route_callback(data: str) -> UiRoute | None:
    parsed = parse_callback(data)
    if parsed.prefix != "pmx:":
        return None

    action = parsed.action
    parts = parsed.parts

    if action == "noop":
        return UiRoute(kind="noop")

    if action == "menu":
        if not parts:
            return UiRoute(kind="show_menu", menu_id=MAIN_MENU_ID)
        head = parts[0]
        if head in submenu_ids() or head in ("ask", "research", "help"):
            if len(parts) == 1:
                if head == "ask":
                    return UiRoute(kind="hermes_prompt", prompt="How can I help?", requires_hermes=True)
                if head == "research":
                    return UiRoute(
                        kind="hermes_prompt",
                        prompt="What market should I research?",
                        requires_hermes=True,
                    )
                if head == "help":
                    return UiRoute(kind="help")
                return UiRoute(kind="show_menu", menu_id=head)
            return UiRoute(kind="action", menu_id=head, sub_action=":".join(parts[1:]))
        return UiRoute(kind="show_menu", menu_id=head)

    if action == "nav" and parts[:1] == ("back",):
        target = parts[1] if len(parts) > 1 else MAIN_MENU_ID
        return UiRoute(kind="show_menu", menu_id=target)

    if action == "refresh":
        menu_id = parts[0] if parts else MAIN_MENU_ID
        return UiRoute(kind="refresh", menu_id=menu_id)

    if action == "toggle" and parts[:1] == ("mode",):
        mode = parts[1] if len(parts) > 1 else "toggle"
        return UiRoute(kind="set_mode", sub_action=mode)

    if action == "quick" and parts:
        quick = parts[0]
        blocked = quick == "trade"
        return UiRoute(kind="quick", sub_action=quick, blocked_in_group=blocked)

    if action == "confirm" and parts[:1] == ("trade",) and len(parts) > 1:
        return UiRoute(kind="trade_confirm", token=parts[1], blocked_in_group=True)

    if action == "cancel" and parts[:1] == ("trade",) and len(parts) > 1:
        return UiRoute(kind="trade_cancel", token=parts[1])

    if action == "page" and len(parts) >= 3:
        menu_id = parts[0]
        direction = parts[1]
        try:
            page = int(parts[2])
        except ValueError:
            page = 0
        return UiRoute(kind="page", menu_id=menu_id, sub_action=direction, page=page)

    return UiRoute(kind="unknown", sub_action=data)


def loading_for_menu(menu_id: str) -> str:
    spec = load_ui_spec().get("loadingMessages", {})
    return spec.get(menu_id, spec.get("market", "Loading…"))
