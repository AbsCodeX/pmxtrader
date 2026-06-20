from __future__ import annotations

from apps.bridge.parse import extract_trade_preview


def test_extract_trade_preview_kalshi_lines():
    stdout = (
        "Event:     USA vs Aus (KXFOO)\n"
        "Outcome:   USA (abc)\n"
        "Price:     0.55  bid=0.54  ask=0.56\n"
        "Fill est:  side=buy amount=1 price=0.56\n"
        "Cross-venue (PMXT Router):\n"
        "  polymarket: Some title\n"
    )
    preview = extract_trade_preview(stdout)
    assert "Event:" in preview
    assert "Price:" in preview
    assert "Fill est:" in preview
    assert "Cross-venue" not in preview


def test_extract_trade_preview_errors():
    stdout = "Error: sidecar not running\nBook:      unavailable (timeout)\n"
    preview = extract_trade_preview(stdout)
    assert "Error:" in preview
    assert "unavailable" in preview


def test_extract_trade_preview_empty():
    assert extract_trade_preview("") == ""
