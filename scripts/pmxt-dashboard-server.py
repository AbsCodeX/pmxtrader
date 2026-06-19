#!/usr/bin/env python3
"""Local pmxtrader dashboard server — serves index.html + safe ./pmx command runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("PMXT_DASHBOARD_PORT", "8765"))
HOST = os.environ.get("PMXT_DASHBOARD_HOST", "127.0.0.1")

# Read-only / safe commands only — no live trades from the web UI
SAFE_COMMANDS: dict[str, list[str]] = {
    "help": ["./pmx", "help"],
    "status": ["./pmx", "status"],
    "warm": ["./pmx", "warm"],
    "balance": ["./pmx", "balance"],
    "positions": ["./pmx", "positions"],
    "poly-balance": ["./pmx", "poly", "balance"],
    "poly-positions": ["./pmx", "poly", "positions"],
    "poly-orders": ["./pmx", "poly", "orders"],
    "providers": ["./scripts/check-providers.sh"],
}

BLOCKED_PREFIXES = ("trade", "sell", "close", "panic", "stop", "cancel")


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


def resolve_command(raw: str) -> list[str] | None:
    text = raw.strip()
    if not text:
        return None
    if text.startswith("./pmx "):
        text = text[6:].strip()
    elif text.startswith("pmx "):
        text = text[4:].strip()
    elif text.startswith("./"):
        return None

    parts = text.split()
    if not parts:
        return None

    key = parts[0].lower()
    for blocked in BLOCKED_PREFIXES:
        if key == blocked or key.startswith("poly") and len(parts) > 1 and parts[1] in (
            "trade", "sell", "close", "cancel", "cancel-all"
        ):
            return None

    alias = "-".join(p.lower() for p in parts[:2]) if len(parts) >= 2 and parts[0].lower() == "poly" else key
    if alias in SAFE_COMMANDS:
        return SAFE_COMMANDS[alias]
    if key in SAFE_COMMANDS:
        return SAFE_COMMANDS[key]

    # Allow: quote EVENT OUTCOME, poly quote SLUG long (read-only research)
    if key == "quote" and len(parts) >= 3:
        return ["./pmx", "quote", parts[1], parts[2], *parts[3:]]
    if len(parts) >= 3 and parts[0].lower() == "poly" and parts[1].lower() == "quote":
        return ["./pmx", "poly", "quote", parts[2], *parts[3:]]
    if key == "link" and len(parts) >= 2:
        return ["./pmx", "link", parts[1], *parts[2:]]
    if len(parts) >= 2 and parts[0].lower() == "poly" and parts[1].lower() == "link":
        return ["./pmx", "poly", "link", parts[2], *parts[3:]]
    if len(parts) >= 2 and parts[0].lower() == "poly" and parts[1].lower() == "markets":
        return ["./pmx", "poly", "markets", *parts[2:]]
    if key == "event" and len(parts) >= 2:
        return ["./pmx", "event", parts[1]]

    return None


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
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
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
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_file(ROOT / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/api/health":
            self._send_json(200, {"ok": True, "root": str(ROOT)})
            return
        if parsed.path == "/api/commands":
            self._send_json(200, {"safe": list(SAFE_COMMANDS.keys())})
            return
        self.send_error(404)

    def do_POST(self) -> None:
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
        argv = resolve_command(str(raw))
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
    server = HTTPServer((HOST, PORT), DashboardHandler)
    print(f"pmxtrader dashboard: http://{HOST}:{PORT}/")
    print(f"Root: {ROOT}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
