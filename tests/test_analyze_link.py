"""Tests for shared apps.bridge.analyze_link."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from apps.bridge import analyze_link as al

ROOT = Path(__file__).resolve().parents[1]


def test_parse_link_url_rejects_bad_scheme():
    result = al.parse_link_url("javascript:alert(1)")
    assert isinstance(result, dict)
    assert result["ok"] is False


def test_parse_link_url_accepts_kalshi_host():
    parsed = al.parse_link_url("https://kalshi.com/markets/foo")
    assert isinstance(parsed, tuple)
    url, venue = parsed
    assert venue == "kalshi"
    assert "kalshi.com" in url


def test_parse_link_url_rejects_unknown_host():
    result = al.parse_link_url("https://evil.example.com/kalshi")
    assert isinstance(result, dict)
    assert result["ok"] is False


def test_detect_venue():
    assert al.detect_venue("https://kalshi.com/x") == "kalshi"
    assert al.detect_venue("https://polymarket.us/market/bar") == "poly"
    assert al.detect_venue("https://evil.example.com") is None


def test_analyze_link_builds_kalshi_argv():
    with patch.object(al, "run_subprocess", return_value={"ok": True, "stdout": "ok"}) as run:
        result = al.analyze_link("https://kalshi.com/markets/foo", root=ROOT)
    assert result["ok"] is True
    assert result["venue"] == "kalshi"
    argv = run.call_args[0][1]
    assert "pmx-link.sh" in argv[1]


def test_analyze_link_builds_poly_argv():
    with patch.object(al, "run_subprocess", return_value={"ok": True, "stdout": "ok"}) as run:
        result = al.analyze_link("https://polymarket.us/market/slug", side="short", root=ROOT)
    assert result["venue"] == "poly"
    argv = run.call_args[0][1]
    assert "polymarket-us-quickstart.sh" in argv[1]
    assert argv[-1] == "short"
