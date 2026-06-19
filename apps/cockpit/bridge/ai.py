"""Hermes one-turn chat for the cockpit."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SESSION_FILE = Path.home() / ".pmxt-cockpit" / "hermes-session.json"

COCKPIT_SYSTEM = """You are the pmxtrader trading cockpit assistant.
The user trades Kalshi and Polymarket US via terminal ./pmx commands (real money).

You CAN suggest read-only commands freely: ./pmx status, ./pmx link, ./pmx poly quote, ./pmx poly markets, ./pmx compare url, ./pmx scout grok.

For LIVE ORDERS (./pmx trade, ./pmx poly trade/sell/close, ./pmx panic): always show the exact command and say the user must confirm in the cockpit — never claim you executed it.

When asked for top markets or volume: suggest ./pmx poly markets QUERY or ./pmx link URL for analysis.

Keep answers concise. Include runnable ./pmx commands on their own lines when helpful.
"""


def _load_session() -> dict:
    if SESSION_FILE.is_file():
        try:
            return json.loads(SESSION_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_session(data: dict) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(data, indent=2))


def chat_turn(message: str, provider: str = "grok") -> dict:
    session = _load_session()
    session_id = session.get("session_id")
    history: list[dict] = session.get("history", [])

    context = COCKPIT_SYSTEM + "\n\nRecent conversation:\n"
    for turn in history[-6:]:
        context += f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')[:800]}\n"
    context += f"\nUser: {message}\n"

    cmd = [
        "hermes",
        "chat",
        "--cli",
        "-t",
        "no_mcp",
        "-Q",
        "-q",
        context,
        "--skills",
        "pmxtrader-scout,pmxtrader-commands,multi-agent-handoff",
        "--provider",
        provider,
    ]
    if session_id:
        cmd.extend(["--resume", session_id])

    env = os.environ.copy()
    env["PMXTRADER_ROOT"] = str(ROOT)
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if not out and err:
            out = err
        if proc.returncode != 0 and not out:
            out = f"Hermes error (exit {proc.returncode}): {err or 'no output'}"

        new_id = session_id
        for line in (proc.stderr or "").splitlines() + (proc.stdout or "").splitlines():
            m = re.search(r"session[_\s]?id[:\s]+([a-f0-9-]+)", line, re.I)
            if m:
                new_id = m.group(1)
                break

        history.append({"user": message, "assistant": out[:4000]})
        _save_session({"session_id": new_id, "history": history[-20:], "provider": provider})

        return {"ok": proc.returncode == 0 or bool(out), "text": out, "session_id": new_id}
    except FileNotFoundError:
        return {
            "ok": False,
            "text": "Hermes not installed. Run: pip install hermes-agent && ./scripts/setup-hermes.sh",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "text": "Hermes timed out (180s). Try a shorter question."}


def clear_session() -> None:
    if SESSION_FILE.is_file():
        SESSION_FILE.unlink(missing_ok=True)
