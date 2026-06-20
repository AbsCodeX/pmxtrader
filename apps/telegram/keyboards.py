"""Inline keyboards for Telegram."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from apps.telegram.briefs import list_active_briefs
from apps.telegram.config import TelegramConfig


def main_menu() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("Status", callback_data="act:status"),
            InlineKeyboardButton("Preflight", callback_data="act:preflight"),
        ],
        [
            InlineKeyboardButton("Scout mode", callback_data="mode:scout"),
            InlineKeyboardButton("Trader mode", callback_data="mode:trader"),
        ],
        [
            InlineKeyboardButton("Briefs", callback_data="act:briefs"),
            InlineKeyboardButton("Go live", callback_data="act:golive"),
        ],
        [
            InlineKeyboardButton("Scenarios", callback_data="act:scenarios"),
            InlineKeyboardButton("Clear chat", callback_data="act:clear"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def trade_confirm(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Review preview", callback_data=f"trade:preview:{token}")],
            [
                InlineKeyboardButton("Execute YES", callback_data=f"trade:exec:{token}"),
                InlineKeyboardButton("Cancel", callback_data=f"trade:cancel:{token}"),
            ],
        ]
    )


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
        rows.append([InlineKeyboardButton("No briefs in briefs/active/", callback_data="act:noop")])
    rows.append([InlineKeyboardButton("Back", callback_data="act:menu")])
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

