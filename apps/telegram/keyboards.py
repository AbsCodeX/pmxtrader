"""Inline keyboards for Telegram — delegates to apps.telegram.ui."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from apps.telegram.briefs import list_active_briefs
from apps.telegram.config import TelegramConfig
from apps.telegram.ui import main_menu as ui_main_menu
from apps.telegram.ui import menu_keyboard as ui_menu_keyboard
from apps.telegram.ui import trade_confirm as ui_trade_confirm


def main_menu() -> InlineKeyboardMarkup:
    return ui_main_menu()


def menu_for(menu_id: str) -> InlineKeyboardMarkup:
    return ui_menu_keyboard(menu_id)


def trade_confirm(token: str) -> InlineKeyboardMarkup:
    return ui_trade_confirm(token)


def briefs_keyboard(cfg: TelegramConfig) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for path in list_active_briefs(cfg)[:8]:
        label = path.name
        if len(label) > 40:
            label = label[:37] + "…"
        rows.append(
            [
                InlineKeyboardButton(label, callback_data=f"brief:show:{path.name}"),
                InlineKeyboardButton("Approve", callback_data=f"brief:approve:{path.name}"),
            ]
        )
    if not rows:
        rows.append([InlineKeyboardButton("No briefs in briefs/active/", callback_data="pmx:noop")])
    rows.append([InlineKeyboardButton("Back", callback_data="pmx:nav:back:main")])
    return InlineKeyboardMarkup(rows)


def link_actions(url: str) -> InlineKeyboardMarkup:
    short = url if len(url) <= 60 else url[:57] + "…"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Scout: {short}", callback_data="link:scout")],
            [
                InlineKeyboardButton("Kalshi quote", callback_data="link:kalshi"),
                InlineKeyboardButton("Poly quote", callback_data="link:poly"),
            ],
        ]
    )
