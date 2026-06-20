"""Inline keyboard builders — mirrors telegram/keyboards.ts."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from apps.telegram.ui.callbacks import build_callback
from apps.telegram.ui.loader import load_ui_spec
from apps.telegram.ui.menus import MAIN_MENU_ID, menu_items
from apps.telegram.ui.miniapps import load_mini_app_urls, mini_app_labels


def _chunk(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _items_to_rows(items: list[dict], *, columns: int = 2) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(item["label"], callback_data=item["callback"])
        for item in items
    ]
    return InlineKeyboardMarkup(_chunk(buttons, columns))


def main_menu() -> InlineKeyboardMarkup:
    return menu_keyboard(MAIN_MENU_ID)


def menu_keyboard(menu_id: str = MAIN_MENU_ID) -> InlineKeyboardMarkup:
    return _items_to_rows(menu_items(menu_id))


def back_refresh(menu_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data=build_callback("nav", "back", MAIN_MENU_ID)),
                InlineKeyboardButton("Refresh", callback_data=build_callback("refresh", menu_id)),
            ]
        ]
    )


def pagination(menu_id: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    row: list[InlineKeyboardButton] = []
    if page > 0:
        row.append(
            InlineKeyboardButton(
                "Prev",
                callback_data=build_callback("page", menu_id, "prev", str(page - 1)),
            )
        )
    row.append(
        InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data=build_callback("noop"))
    )
    if page < total_pages - 1:
        row.append(
            InlineKeyboardButton(
                "Next",
                callback_data=build_callback("page", menu_id, "next", str(page + 1)),
            )
        )
    return InlineKeyboardMarkup([row])


def confirm_cancel(confirm_data: str, cancel_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Confirm", callback_data=confirm_data),
                InlineKeyboardButton("Cancel", callback_data=cancel_data),
            ]
        ]
    )


def trade_confirm(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Review preview", callback_data=f"trade:preview:{token}")],
            [
                InlineKeyboardButton(
                    "Confirm execute",
                    callback_data=build_callback("confirm", "trade", token),
                ),
                InlineKeyboardButton(
                    "Cancel",
                    callback_data=build_callback("cancel", "trade", token),
                ),
            ],
        ]
    )


def quick_actions() -> InlineKeyboardMarkup:
    spec = load_ui_spec()
    actions = spec.get("quickActions", [])
    row = [
        InlineKeyboardButton(
            action.capitalize(),
            callback_data=build_callback("quick", action),
        )
        for action in actions
    ]
    return InlineKeyboardMarkup([row])


def mini_app_row() -> InlineKeyboardMarkup:
    urls = load_mini_app_urls()
    labels = mini_app_labels()
    buttons: list[InlineKeyboardButton] = []
    for key, label in labels.items():
        url = getattr(urls, key)
        buttons.append(
            InlineKeyboardButton(label, web_app=WebAppInfo(url=url))
        )
    return InlineKeyboardMarkup(_chunk(buttons, 2))
