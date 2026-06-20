"""Tests for dashboard /api/safety endpoint."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def dashboard_module(monkeypatch):
    monkeypatch.setenv("PMXT_DASHBOARD_TOKEN", "test-token")
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "pmxt_dashboard_server",
        root / "scripts" / "pmxt-dashboard-server.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_safety_endpoint_requires_token(dashboard_module):
    handler_cls = dashboard_module.DashboardHandler
    sent: list[tuple[int, dict]] = []

    class FakeHandler(handler_cls):
        def __init__(self):
            self.headers = {}
            self.path = "/api/safety"

        def _check_token(self):
            return False

        def _send_json(self, code, payload):
            sent.append((code, payload))

    FakeHandler().do_GET()
    assert sent[0][0] == 403


def test_safety_endpoint_payload(dashboard_module, tmp_path: Path):
    handler_cls = dashboard_module.DashboardHandler
    sent: list[dict] = []

    class FakeHandler(handler_cls):
        def __init__(self):
            self.headers = {"X-Pmxtrader-Token": "test-token"}
            self.path = "/api/safety"

        def _check_token(self):
            return True

        def _send_json(self, code, payload):
            sent.append(payload)

    with patch.object(dashboard_module, "ROOT", tmp_path):
        FakeHandler().do_GET()

    assert sent
    body = sent[0]
    assert body["ok"] is True
    assert body["killSwitch"] == "OFF"
    assert body["readOnly"] is True
    assert body["maxTradeContracts"] == 10.0
