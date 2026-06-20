"""Tests for Batch E API / integration hardening."""

from __future__ import annotations

from apps.cockpit.bridge import pmx


def test_cockpit_pmx_env_is_minimal(monkeypatch):
    monkeypatch.setenv("SECRET_SHOULD_NOT_LEAK", "sk-test")
    monkeypatch.setenv("PATH", "/usr/bin")
    env = pmx.env()
    assert "SECRET_SHOULD_NOT_LEAK" not in env
    assert env["PMXTRADER_ROOT"] == str(pmx.ROOT)
    assert env["PMXT_DIR"] == str(pmx.ROOT / "pmxt")
    assert env["PATH"] == "/usr/bin"
