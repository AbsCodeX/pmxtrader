"""Smoke tests for ./pmx CLI routing (scripts/pmx.sh)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_agent_propose_passes_args_to_trade_proposal():
    """agent propose must not double-shift away the first argument."""
    proc = subprocess.run(
        [str(ROOT / "pmx"), "agent", "propose", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "Generate formatted trade proposal" in proc.stdout


def test_agent_propose_recognizes_fair_flag():
    proc = subprocess.run(
        [
            str(ROOT / "pmx"),
            "agent",
            "propose",
            "--fair",
            "0.62",
            "--ask",
            "0.50",
            "--event",
            "TEST-EVENT",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    combined = proc.stdout + proc.stderr
    assert "required: --fair" not in combined
    assert "unrecognized arguments: 0.62" not in combined


def test_top_level_propose_passes_args():
    proc = subprocess.run(
        [str(ROOT / "pmx"), "propose", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "Generate formatted trade proposal" in proc.stdout
