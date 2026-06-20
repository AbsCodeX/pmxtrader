"""pmxtrader Telegram UI layer — Python adapter for telegram-ui/ui-spec.json."""

from apps.telegram.ui.loader import load_ui_spec
from apps.telegram.ui.menus import menu_items, menu_title
from apps.telegram.ui.keyboards import (
    main_menu,
    menu_keyboard,
    trade_confirm,
    confirm_cancel,
    pagination,
    quick_actions,
    mini_app_row,
)
from apps.telegram.ui.cards import (
    market_card,
    trade_confirm_card,
    agent_status_card,
    alert_card,
    portfolio_card,
    loading_message,
    error_message,
    help_card,
    main_menu_message,
)
from apps.telegram.ui.tables import markets_table, positions_table, agent_logs_table
from apps.telegram.ui.callbacks import build_callback, parse_callback, CALLBACK_PREFIX
from apps.telegram.ui.permissions import (
    PermissionConfig,
    load_permissions,
    chat_is_admin,
    trading_allowed_in_chat,
)
from apps.telegram.ui.miniapps import load_mini_app_urls
from apps.telegram.ui.router import route_callback

__all__ = [
    "load_ui_spec",
    "menu_items",
    "menu_title",
    "main_menu",
    "menu_keyboard",
    "trade_confirm",
    "confirm_cancel",
    "pagination",
    "quick_actions",
    "mini_app_row",
    "market_card",
    "trade_confirm_card",
    "agent_status_card",
    "alert_card",
    "portfolio_card",
    "loading_message",
    "error_message",
    "help_card",
    "main_menu_message",
    "markets_table",
    "positions_table",
    "agent_logs_table",
    "build_callback",
    "parse_callback",
    "CALLBACK_PREFIX",
    "PermissionConfig",
    "load_permissions",
    "chat_is_admin",
    "trading_allowed_in_chat",
    "load_mini_app_urls",
    "route_callback",
]
