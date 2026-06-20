"""Tests for dashboard security helpers."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from apps.bridge.dashboard_security import (
    DASHBOARD_CSP,
    inject_dashboard_token,
    minimal_subprocess_env,
    resolve_bind_host,
    write_secret_token,
)


def test_resolve_bind_host_localhost():
    assert resolve_bind_host("127.0.0.1") == "127.0.0.1"


def test_resolve_bind_host_refuses_wide_bind(monkeypatch):
    monkeypatch.delenv("PMXT_DASHBOARD_INSECURE_BIND", raising=False)
    with pytest.raises(SystemExit):
        resolve_bind_host("0.0.0.0")


def test_resolve_bind_host_allows_wide_with_flag():
    assert resolve_bind_host("0.0.0.0", insecure_bind="1") == "0.0.0.0"


def test_minimal_subprocess_env_strips_secrets():
    root = Path("/tmp/pmxtrader")
    env = minimal_subprocess_env(
        root,
        base={
            "PATH": "/usr/bin",
            "SECRET_API_KEY": "sk-should-not-leak",
            "PMXT_CLI_BIN": "pmxt",
        },
    )
    assert env["PATH"] == "/usr/bin"
    assert env["PMXTRADER_ROOT"] == str(root)
    assert "SECRET_API_KEY" not in env


def test_inject_dashboard_token():
    html = "<html><head></head><body></body></html>"
    out = inject_dashboard_token(html, "abc123")
    assert "window.__PMXT_DASHBOARD_TOKEN__=\"abc123\"" in out


def test_write_secret_token_mode(tmp_path: Path):
    path = tmp_path / "token"
    write_secret_token(path, "secret")
    assert path.read_text().strip() == "secret"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_dashboard_csp_present():
    assert "default-src 'self'" in DASHBOARD_CSP
    assert "frame-ancestors 'none'" in DASHBOARD_CSP
