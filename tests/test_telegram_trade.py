"""Telegram trade token and brief approval tests."""

from __future__ import annotations

from pathlib import Path

from apps.bridge.telegram_trade import (
    chat_is_allowed,
    consume_telegram_trade_token,
    create_pending_trade,
    get_pending,
)
from apps.telegram.briefs import approve_brief, brief_is_approved


def test_chat_allowlist(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "123,456")
    assert chat_is_allowed("123")
    assert not chat_is_allowed("999")


def test_pending_trade_lifecycle(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "42")
    pending = create_pending_trade(
        chat_id="42",
        command=["trade", "MARKET", "USA", "1"],
        preview="preview text",
        venue="kalshi",
        ttl_seconds=60,
    )
    loaded = get_pending(pending.token)
    assert loaded is not None
    assert loaded.command == ["trade", "MARKET", "USA", "1"]


def test_consume_telegram_token(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "7")
    pending = create_pending_trade(
        chat_id="7",
        command=["poly", "trade", "slug", "long", "1"],
        preview="p",
        venue="polymarket_us",
    )
    monkeypatch.setenv("PMX_TELEGRAM_CONFIRM", "1")
    monkeypatch.setenv("PMX_TELEGRAM_TRADE_TOKEN", pending.token)
    monkeypatch.setenv("PMX_TELEGRAM_CHAT_ID", "7")
    result = consume_telegram_trade_token(pending.token, chat_id="7")
    assert result.ok
    assert get_pending(pending.token) is None


def test_approve_brief(tmp_path: Path):
    brief = tmp_path / "test-brief.md"
    brief.write_text(
        "---\nid: test\napproved: false\n---\n\n# Title\n",
        encoding="utf-8",
    )
    assert not brief_is_approved(brief)
    ok, _ = approve_brief(brief)
    assert ok
    assert brief_is_approved(brief)
