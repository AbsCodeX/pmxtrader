"""Run ./pmx and related scripts from the cockpit."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from apps.bridge.commands import classify_command, extract_pmx_commands, is_palette_allowed

ROOT = Path(__file__).resolve().parents[3]

__all__ = [
    "ROOT",
    "analyze_link",
    "classify_command",
    "env",
    "extract_pmx_commands",
    "is_palette_allowed",
    "run_argv",
    "run_pmx",
    "run_script",
]


def env() -> dict[str, str]:
    e = os.environ.copy()
    e["PMXTRADER_ROOT"] = str(ROOT)
    e["PMXT_DIR"] = str(ROOT / "pmxt")
    return e


def run_argv(argv: list[str], timeout: int = 120) -> dict:
    try:
        proc = subprocess.run(
            argv,
            cwd=ROOT,
            env=env(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "command": " ".join(argv),
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timed out", "command": " ".join(argv), "stdout": "", "stderr": ""}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "command": " ".join(argv), "stdout": "", "stderr": ""}


def run_pmx(*args: str, timeout: int = 120) -> dict:
    return run_argv([str(ROOT / "pmx"), *args], timeout=timeout)


def run_script(relative: str, *args: str, timeout: int = 120) -> dict:
    return run_argv(["bash", str(ROOT / "scripts" / relative), *args], timeout=timeout)


def analyze_link(url: str, outcome: str = "USA", side: str = "long", size: float = 1) -> dict:
    lower = url.lower()
    if "kalshi" in lower:
        argv = ["bash", str(ROOT / "scripts" / "pmx-link.sh"), url.strip(), outcome, str(int(size) if size == int(size) else size)]
        venue = "kalshi"
    elif "polymarket" in lower:
        argv = ["bash", str(ROOT / "scripts" / "polymarket-us-quickstart.sh"), "link", url.strip(), side]
        venue = "poly"
    else:
        return {"ok": False, "error": "Paste a kalshi.com or polymarket.us URL", "stdout": "", "stderr": ""}
    result = run_argv(argv, timeout=180)
    result["venue"] = venue
    return result
