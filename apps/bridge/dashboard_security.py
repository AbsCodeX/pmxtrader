"""Dashboard server security helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path

LOCALHOST_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

# Minimal env keys passed to dashboard subprocesses (scripts load pmxt/.env themselves).
SUBPROCESS_ENV_KEYS = frozenset({
    "PATH",
    "HOME",
    "USER",
    "LANG",
    "LC_ALL",
    "TMPDIR",
    "PMXT_DASHBOARD_TOKEN",
    "PMXT_CLI_BIN",
    "PMXT_CLI_MODE",
    "PMXT_CLI_SCRIPT",
    "KALSHI_BASE_URL",
    "PMX_READ_ONLY",
    "PMX_MAX_TRADE_CONTRACTS",
    "PMX_TRADE_CONFIRM",
    "PMX_DRY_RUN",
})


def resolve_bind_host(
    host: str | None = None,
    *,
    insecure_bind: str | None = None,
) -> str:
    """Default loopback-only; require PMXT_DASHBOARD_INSECURE_BIND=1 for wide bind."""
    bind = (host or os.environ.get("PMXT_DASHBOARD_HOST") or "127.0.0.1").strip()
    if bind in LOCALHOST_HOSTS:
        return bind
    flag = insecure_bind if insecure_bind is not None else os.environ.get("PMXT_DASHBOARD_INSECURE_BIND", "")
    if flag == "1":
        return bind
    raise SystemExit(
        f"Refusing to bind dashboard to {bind!r}. "
        "Use 127.0.0.1 or set PMXT_DASHBOARD_INSECURE_BIND=1 to override."
    )


def minimal_subprocess_env(root: Path, base: dict[str, str] | None = None) -> dict[str, str]:
    """Strip parent env before spawning ./pmx or helper scripts."""
    src = base if base is not None else os.environ
    env = {k: v for k, v in src.items() if k in SUBPROCESS_ENV_KEYS and v is not None}
    env["PMXTRADER_ROOT"] = str(root)
    env["PMXT_DIR"] = str(root / "pmxt")
    return env


def write_secret_token(path: Path, token: str) -> None:
    path.write_text(token + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def inject_dashboard_token(html: str, token: str) -> str:
    """Inject session token into served index.html (not exposed via /api/health)."""
    snippet = f"<script>window.__PMXT_DASHBOARD_TOKEN__={json.dumps(token)};</script>"
    if "</head>" in html:
        return html.replace("</head>", snippet + "\n</head>", 1)
    return snippet + html


DASHBOARD_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "connect-src 'self'; "
    "img-src 'self' data:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'"
)


def send_security_headers(handler) -> None:
    """Attach baseline security headers to dashboard HTTP responses."""
    handler.send_header("Content-Security-Policy", DASHBOARD_CSP)
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("X-Frame-Options", "DENY")
    handler.send_header("Referrer-Policy", "same-origin")
