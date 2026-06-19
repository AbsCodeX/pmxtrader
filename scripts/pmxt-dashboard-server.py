#!/usr/bin/env python3
"""Local pmxtrader dashboard server — serves index.html + safe ./pmx command runner."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.bridge.commands import resolve_dashboard_command  # noqa: E402

PORT = int(os.environ.get("PMXT_DASHBOARD_PORT", "8765"))
HOST = os.environ.get("PMXT_DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_TOKEN = os.environ.get("PMXT_DASHBOARD_TOKEN") or secrets.token_urlsafe(24)
TOKEN_FILE = ROOT / ".pmxt-dashboard.token"


def detect_venue(url: str) -> str | None:
    lower = url.strip().lower()
    if "kalshi" in lower:
        return "kalshi"
    if "polymarket" in lower:
        return "poly"
    return None


def analyze_link(
    url: str,
    outcome: str | None = None,
    side: str | None = None,
    size: float = 1.0,
) -> dict:
    raw = url.strip()
    if not raw:
        return {"ok": False, "error": "URL is required"}

    if raw.startswith("http://") or raw.startswith("https://"):
        normalized = raw
    else:
        normalized = "https://" + raw.lstrip("/")

    venue = detect_venue(normalized)
    if venue == "kalshi":
        argv = ["bash", str(ROOT / "scripts" / "pmx-link.sh"), normalized]
        label = (outcome or "USA").strip()
        if label:
            argv.append(label)
        argv.append(str(int(size) if size == int(size) else size))
    elif venue == "poly":
        argv = [
            "bash",
            str(ROOT / "scripts" / "polymarket-us-quickstart.sh"),
            "link",
            normalized,
            (side or "long").strip().lower() or "long",
        ]
    else:
        return {
            "ok": False,
            "error": "Unrecognized link — paste a kalshi.com or polymarket.us URL",
        }

    result = run_pmx(argv, timeout=180)
    result["venue"] = venue
    result["url"] = normalized
    return result


def run_pmx(argv: list[str], timeout: int = 120) -> dict:
    env = os.environ.copy()
    env["PMXTRADER_ROOT"] = str(ROOT)
    env["PMXT_DIR"] = str(ROOT / "pmxt")
    try:
        proc = subprocess.run(
            argv,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "exitCode": proc.returncode,
            "command": " ".join(argv),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Command timed out", "command": " ".join(argv)}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "command": " ".join(argv)}


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "pmxtrader-dashboard/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _check_token(self) -> bool:
        token = self.headers.get("X-Pmxtrader-Token", "")
        return token == DASHBOARD_TOKEN

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_response(405)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_file(ROOT / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/api/health":
            self._send_json(200, {"ok": True, "root": str(ROOT), "token": DASHBOARD_TOKEN})
            return
        if parsed.path == "/api/commands":
            from apps.bridge.commands import SAFE_COMMANDS

            self._send_json(200, {"safe": list(SAFE_COMMANDS.keys())})
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if not self._check_token():
            self._send_json(403, {"ok": False, "error": "Invalid or missing X-Pmxtrader-Token header"})
            return

        parsed = urlparse(self.path)
        if parsed.path not in ("/api/run", "/api/analyze"):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "Invalid JSON"})
            return

        if parsed.path == "/api/analyze":
            url = str(body.get("url", "")).strip()
            outcome = body.get("outcome")
            side = body.get("side")
            try:
                size = float(body.get("size", 1))
            except (TypeError, ValueError):
                size = 1.0
            result = analyze_link(
                url,
                str(outcome).strip() if outcome else None,
                str(side).strip() if side else None,
                size,
            )
            self._send_json(200, result)
            return

        raw = body.get("command", "")
        argv = resolve_dashboard_command(str(raw))
        if not argv:
            self._send_json(400, {
                "ok": False,
                "error": "Command not allowed from dashboard. Use real terminal for trades.",
                "hint": "Safe: status, balance, poly balance, quote EVENT USA 1, poly quote SLUG long, or use Link analyzer",
            })
            return
        result = run_pmx(argv)
        self._send_json(200, result)


def main() -> None:
    os.chdir(ROOT)
    TOKEN_FILE.write_text(DASHBOARD_TOKEN + "\n")
    server = HTTPServer((HOST, PORT), DashboardHandler)
    print(f"pmxtrader dashboard: http://{HOST}:{PORT}/")
    print(f"Root: {ROOT}")
    print(f"API token written to: {TOKEN_FILE}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
