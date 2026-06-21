"""Run ./pmx and related scripts from the cockpit."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlparse

from apps.bridge.commands import classify_command, extract_pmx_commands, is_palette_allowed
from apps.bridge.dashboard_security import minimal_subprocess_env

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = (ROOT / "scripts").resolve()

_KALSHI_HOSTS = frozenset({"kalshi.com", "www.kalshi.com", "demo.kalshi.com"})
_POLY_HOSTS = frozenset({"polymarket.us", "www.polymarket.us"})

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


def _parse_link_url(url: str) -> tuple[str, str] | dict:
    raw = url.strip()
    if not raw:
        return {"ok": False, "error": "Paste a kalshi.com or polymarket.us URL", "stdout": "", "stderr": ""}
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw.lstrip("/")
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return {"ok": False, "error": "URL must use http(s) with a valid host", "stdout": "", "stderr": ""}
    host = parsed.hostname.lower()
    if host in _KALSHI_HOSTS or host.endswith(".kalshi.com"):
        return raw, "kalshi"
    if host in _POLY_HOSTS or host.endswith(".polymarket.us"):
        return raw, "poly"
    return {
        "ok": False,
        "error": "Paste a kalshi.com or polymarket.us URL",
        "stdout": "",
        "stderr": "",
    }


def analyze_link(url: str, outcome: str = "USA", side: str = "long", size: float = 1) -> dict:
    parsed = _parse_link_url(url)
    if isinstance(parsed, dict):
        return parsed
    normalized, venue = parsed
    if venue == "kalshi":
        argv = [
            "bash",
            str(ROOT / "scripts" / "pmx-link.sh"),
            normalized,
            outcome,
            str(int(size) if size == int(size) else size),
        ]
    else:
        argv = [
            "bash",
            str(ROOT / "scripts" / "polymarket-us-quickstart.sh"),
            "link",
            normalized,
            side,
        ]
    result = run_argv(argv, timeout=180)
    result["venue"] = venue
    result["url"] = normalized
    if result.get("stdout"):
        from apps.bridge.parse import extract_trade_preview

        preview = extract_trade_preview(result["stdout"])
        if preview:
            result["preview"] = preview
    return result
