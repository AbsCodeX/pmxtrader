"""Run ./pmx and related scripts from the cockpit."""

from __future__ import annotations

import subprocess
from pathlib import Path

from apps.bridge.analyze_link import analyze_link as _analyze_link
from apps.bridge.commands import classify_command, extract_pmx_commands, is_palette_allowed
from apps.bridge.dashboard_security import minimal_subprocess_env

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = (ROOT / "scripts").resolve()

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
    "trade_command_needs_assume_yes",
]


def env() -> dict[str, str]:
    return minimal_subprocess_env(ROOT)


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


def trade_command_needs_assume_yes(args: tuple[str, ...] | list[str]) -> bool:
    """True when pmx would prompt for interactive YES on stdin (live trade paths)."""
    if not args:
        return False
    head = args[0].lower()
    if head == "trade":
        return True
    if head == "poly" and len(args) > 1 and args[1].lower() in ("trade", "sell", "close"):
        return True
    return False


def run_pmx(*args: str, timeout: int = 120, assume_yes: bool = False) -> dict:
    argv: list[str] = [str(ROOT / "pmx"), *args]
    if assume_yes and trade_command_needs_assume_yes(args) and "--yes" not in args and "-y" not in args:
        argv.append("--yes")
    return run_argv(argv, timeout=timeout)


def run_script(relative: str, *args: str, timeout: int = 120) -> dict:
    if not relative or ".." in relative or relative.startswith(("/", "\\")):
        return {
            "ok": False,
            "error": "Invalid script path",
            "command": relative,
            "stdout": "",
            "stderr": "",
        }
    script = (ROOT / "scripts" / relative).resolve()
    try:
        script.relative_to(SCRIPTS_DIR)
    except ValueError:
        return {
            "ok": False,
            "error": "Script outside scripts/",
            "command": relative,
            "stdout": "",
            "stderr": "",
        }
    if not script.is_file():
        return {
            "ok": False,
            "error": f"Script not found: {relative}",
            "command": relative,
            "stdout": "",
            "stderr": "",
        }
    return run_argv(["bash", str(script), *args], timeout=timeout)


def analyze_link(url: str, outcome: str = "USA", side: str = "long", size: float = 1) -> dict:
    return _analyze_link(
        url,
        outcome=outcome,
        side=side,
        size=size,
        root=ROOT,
        runner=lambda argv, timeout: run_argv(argv, timeout=timeout),
    )
