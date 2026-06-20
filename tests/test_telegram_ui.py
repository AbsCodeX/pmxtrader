"""Tests for telegram-ui/ UI spec and apps/telegram/ui Python adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "telegram-ui" / "ui-spec.json"


@pytest.fixture
def spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_ui_spec_exists_and_version(spec: dict):
    assert spec["version"] == "1.0.0"
    assert spec["callbackPrefix"] == "pmx:"


def test_main_menu_has_eight_sections(spec: dict):
    items = spec["mainMenu"]["items"]
    labels = [item["label"] for item in items]
    assert len(items) == 8
    assert "Ask Hermes" in labels
    assert "Prediction Markets" in labels
    assert "Agent Tools" in labels
    assert "Help" in labels


def test_submenus_nested(spec: dict):
    subs = spec["subMenus"]
    assert "markets" in subs
    assert "portfolio" in subs
    assert "agents" in subs
    assert "alerts" in subs
    assert "settings" in subs
    for key in ("markets", "portfolio", "agents", "alerts", "settings"):
        back = [i for i in subs[key]["items"] if i["label"] == "Back"]
        assert back, f"{key} missing Back button"


def test_callbacks_use_pmx_prefix(spec: dict):
    all_items = list(spec["mainMenu"]["items"])
    for sub in spec["subMenus"].values():
        all_items.extend(sub["items"])
    for item in all_items:
        cb = item["callback"]
        assert cb.startswith("pmx:") or cb.startswith("act:"), cb
        assert len(cb) <= 64, cb


def test_build_and_parse_callback():
    from apps.telegram.ui.callbacks import build_callback, parse_callback

    data = build_callback("menu", "markets", "trending")
    assert data == "pmx:menu:markets:trending"
    parsed = parse_callback(data)
    assert parsed.action == "menu"
    assert parsed.parts == ("markets", "trending")


def test_route_main_menu():
    from apps.telegram.ui.router import route_callback

    route = route_callback("pmx:menu:markets")
    assert route is not None
    assert route.kind == "show_menu"
    assert route.menu_id == "markets"


def test_route_trade_blocked_in_group():
    from apps.telegram.ui.router import route_callback

    route = route_callback("pmx:quick:trade")
    assert route is not None
    assert route.blocked_in_group is True


def test_permissions_group_trading(monkeypatch):
    from apps.telegram.ui.permissions import load_permissions, trading_allowed_in_chat

    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "99")
    monkeypatch.setenv("PMX_TELEGRAM_GROUP_TRADING", "0")
    cfg = load_permissions()
    assert trading_allowed_in_chat("99", "private", cfg)
    assert not trading_allowed_in_chat("99", "group", cfg)

    monkeypatch.setenv("PMX_TELEGRAM_GROUP_TRADING", "1")
    cfg = load_permissions()
    assert trading_allowed_in_chat("99", "group", cfg)


def test_market_card_format():
    from apps.telegram.ui.cards import market_card

    text = market_card(
        title="USA vs AUS",
        venue="Kalshi",
        outcome="USA",
        price="62¢",
        url="https://kalshi.com/markets/example",
    )
    assert "USA vs AUS" in text
    assert "Kalshi" in text


def test_trade_confirm_card_requires_confirm_language():
    from apps.telegram.ui.cards import trade_confirm_card

    text = trade_confirm_card(
        venue="Kalshi",
        market="KXTEST",
        outcome="YES",
        side="buy",
        size="1",
        est_cost="$0.62",
        command="./pmx trade KXTEST YES 1",
    )
    assert "Confirm" in text
    assert "./pmx trade" in text


def test_markets_table_monospace():
    from apps.telegram.ui.tables import markets_table

    text = markets_table(
        [{"symbol": "KXTEST", "outcome": "YES", "bid": "60", "ask": "62", "vol": "1.2k"}]
    )
    assert "```" in text
    assert "KXTEST" in text


def test_menu_keyboard_row_count():
    from apps.telegram.ui.keyboards import main_menu

    markup = main_menu()
    assert len(markup.inline_keyboard) == 4  # 8 items / 2 columns


def test_trade_confirm_has_two_step_buttons():
    from apps.telegram.ui.keyboards import trade_confirm

    markup = trade_confirm("tok123")
    flat = [btn.text for row in markup.inline_keyboard for btn in row]
    assert "Review preview" in flat
    assert "Confirm execute" in flat
    assert "Cancel" in flat


def test_mini_app_urls_from_env(monkeypatch):
    from apps.telegram.ui.miniapps import load_mini_app_urls

    monkeypatch.setenv("PMX_TELEGRAM_MINIAPP_DASHBOARD", "https://dash.example/pmx")
    urls = load_mini_app_urls()
    assert urls.dashboard == "https://dash.example/pmx"


def test_loading_and_error_messages():
    from apps.telegram.ui.cards import error_message, loading_message

    assert "Checking" in loading_message("market")
    assert "Error" in error_message("API", "timeout")
