"""Tests for PMXT CLI argv resolution."""

from apps.bridge.pmxt_cli import pmxt_argv


def test_pmxt_argv_global(monkeypatch):
    monkeypatch.delenv("PMXT_CLI_MODE", raising=False)
    monkeypatch.setenv("PMXT_CLI_BIN", "pmxt")
    assert pmxt_argv(["kalshi", "orders", "open"]) == ["pmxt", "kalshi", "orders", "open"]


def test_pmxt_argv_vendored(monkeypatch, tmp_path):
    script = str(tmp_path / "pmxt.js")
    monkeypatch.setenv("PMXT_CLI_MODE", "vendored")
    monkeypatch.setenv("PMXT_CLI_SCRIPT", script)
    assert pmxt_argv(["kalshi", "order", "cancel"], root=tmp_path) == [
        "node",
        script,
        "kalshi",
        "order",
        "cancel",
    ]
