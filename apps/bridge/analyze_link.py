"""Shared link analyzer for dashboard and cockpit — kalshi.com / polymarket.us URLs."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

from apps.bridge.dashboard_security import minimal_subprocess_env
from apps.bridge.parse import extract_trade_preview

_KALSHI_HOSTS = frozenset({"kalshi.com", "www.kalshi.com", "demo.kalshi.com"})
_POLY_HOSTS = frozenset({"polymarket.us", "www.polymarket.us"})

RunResult = dict[str, object]
Runner = Callable[[list[str], int], RunResult]

__all__ = [
    "analyze_link",
    "detect_venue",
    "parse_link_url",
    "run_subprocess",
]


def detect_venue(url: str) -> str | None:
    """Return ``kalshi`` or ``poly`` when the URL host matches; else ``None``."""
    parsed = parse_link_url(url)
    if isinstance(parsed, dict):
        return None
    _, venue = parsed
    return venue


def parse_link_url(url: str) -> tuple[str, str] | dict[str, object]:
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


def build_link_argv(
    root: Path,
    normalized: str,
    venue: str,
    *,
    outcome: str = "USA",
    side: str = "long",
    size: float = 1,
) -> list[str]:
    if venue == "kalshi":
        return [
            "bash",
            str(root / "scripts" / "pmx-link.sh"),
            normalized,
            outcome,
            str(int(size) if size == int(size) else size),
        ]
    return [
        "bash",
        str(root / "scripts" / "polymarket-us-quickstart.sh"),
        "link",
        normalized,
        side,
    ]


def run_subprocess(root: Path, argv: list[str], timeout: int = 120) -> RunResult:
    try:
        proc = subprocess.run(
            argv,
            cwd=root,
            env=minimal_subprocess_env(root),
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


def analyze_link(
    url: str,
    outcome: str = "USA",
    side: str = "long",
    size: float = 1,
    *,
    root: Path,
    runner: Runner | None = None,
) -> RunResult:
    parsed = parse_link_url(url)
    if isinstance(parsed, dict):
        return parsed
    normalized, venue = parsed
    argv = build_link_argv(
        root,
        normalized,
        venue,
        outcome=(outcome or "USA").strip() or "USA",
        side=(side or "long").strip().lower() or "long",
        size=size,
    )
    run = runner or (lambda a, t: run_subprocess(root, a, timeout=t))
    result = run(argv, 180)
    result["venue"] = venue
    result["url"] = normalized
    stdout = result.get("stdout")
    if isinstance(stdout, str) and stdout:
        preview = extract_trade_preview(stdout)
        if preview:
            result["preview"] = preview
    return result
