"""Hermes bridge for Telegram — fast one-turn chat with session resume."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from apps.telegram.config import TelegramConfig

SESSION_FILE = Path.home() / ".pmxt-telegram" / "hermes-session.json"

TELEGRAM_SYSTEM = """You are Hermes on Telegram for pmxtrader (Kalshi + Polymarket US, real money).

Style:
- Plain language, short paragraphs (Telegram mobile).
- When sharing links, repeat the full URL on its own line.
- Suggest tap-friendly next steps: Quote, Scout brief, Approve, Execute.
- For live orders: show exact ./pmx command on its own line; say user must tap Confirm buttons — never claim you executed.

Modes:
- Scout: research, compare, draft briefs (no orders).
- Trader: from approved brief only; max 2 prep commands then present trade command.

Read-only ./pmx is fine to suggest: status, quote, poly quote, link, compare, markets.
Live: trade, poly trade/sell/close, panic — always require human Confirm in Telegram.

Keep answers under ~1200 characters when possible. Use bullet lists for clarity.
"""


def _load_session() -> dict:
    if not SESSION_FILE.is_file():
        return {}
    try:
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_session(data: dict) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        SESSION_FILE.chmod(0o600)
    except OSError:
        pass


def clear_session() -> None:
    if SESSION_FILE.is_file():
        SESSION_FILE.unlink(missing_ok=True)


def ask_hermes(
    cfg: TelegramConfig,
    message: str,
    *,
    mode: str = "scout",
    extra_context: str = "",
) -> dict:
    session = _load_session()
    session_id = session.get("session_id")
    history: list[dict] = session.get("history", [])
    skills = cfg.hermes_scout_skills if mode == "scout" else cfg.hermes_trader_skills

    context = TELEGRAM_SYSTEM + f"\n\nCurrent mode: {mode.upper()}\n"
    if extra_context:
        context += extra_context + "\n"
    context += "\nRecent conversation:\n"
    for turn in history[-4:]:
        context += f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')[:600]}\n"
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
        skills,
        "--provider",
        cfg.hermes_provider,
    ]
    if session_id:
        cmd.extend(["--resume", session_id])

    env = os.environ.copy()
    env["PMXTRADER_ROOT"] = str(cfg.root)
    timeout = int(os.environ.get("TELEGRAM_HERMES_TIMEOUT", "120"))

    try:
        proc = subprocess.run(
            cmd,
            cwd=cfg.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if not out and err:
            out = err
        if proc.returncode != 0 and not out:
            out = f"Hermes error (exit {proc.returncode}): {err or 'no output'}"

        new_id = session_id
        for line in (proc.stderr or "").splitlines() + (proc.stdout or "").splitlines():
            match = re.search(r"session[_\s]?id[:\s]+([a-f0-9-]+)", line, re.I)
            if match:
                new_id = match.group(1)
                break

        history.append({"user": message, "assistant": out[:4000], "mode": mode})
        _save_session({"session_id": new_id, "history": history[-24:], "provider": cfg.hermes_provider})

        return {"ok": proc.returncode == 0 or bool(out), "text": out, "session_id": new_id}
    except FileNotFoundError:
        return {
            "ok": False,
            "text": "Hermes not installed. Run: pip install hermes-agent && ./scripts/setup-hermes.sh",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "text": f"Hermes timed out ({timeout}s). Try a shorter message."}
