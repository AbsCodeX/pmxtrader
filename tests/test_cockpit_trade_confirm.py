"""Cockpit live trade confirmation — no stdin hang on YES prompt."""

from unittest.mock import patch

from apps.cockpit.bridge import pmx


def test_trade_command_needs_assume_yes():
    assert pmx.trade_command_needs_assume_yes(("trade", "MKT", "OUT", "1"))
    assert pmx.trade_command_needs_assume_yes(("poly", "trade", "slug", "long", "1"))
    assert pmx.trade_command_needs_assume_yes(("poly", "sell", "slug", "long", "100"))
    assert not pmx.trade_command_needs_assume_yes(("balance",))
    assert not pmx.trade_command_needs_assume_yes(("poly", "balance"))


def test_run_pmx_appends_yes_after_cockpit_confirm():
    with patch("apps.cockpit.bridge.pmx.run_argv") as mock_run:
        mock_run.return_value = {"ok": True, "stdout": "ok", "stderr": ""}
        pmx.run_pmx("trade", "MKT", "OUT", "1", assume_yes=True)
        argv = mock_run.call_args[0][0]
        assert argv[-1] == "--yes"
        assert "trade" in argv


def test_run_pmx_does_not_duplicate_yes():
    with patch("apps.cockpit.bridge.pmx.run_argv") as mock_run:
        mock_run.return_value = {"ok": True, "stdout": "", "stderr": ""}
        pmx.run_pmx("trade", "MKT", "OUT", "1", "--yes", assume_yes=True)
        argv = mock_run.call_args[0][0]
        assert argv.count("--yes") == 1


def test_run_pmx_safe_command_ignores_assume_yes():
    with patch("apps.cockpit.bridge.pmx.run_argv") as mock_run:
        mock_run.return_value = {"ok": True, "stdout": "", "stderr": ""}
        pmx.run_pmx("balance", assume_yes=True)
        argv = mock_run.call_args[0][0]
        assert "--yes" not in argv
