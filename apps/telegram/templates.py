"""Telegram message templates."""

from __future__ import annotations


def welcome() -> str:
    return (
        "pmxtrader on Telegram\n\n"
        "Talk in plain language — Hermes handles research and trade prep.\n"
        "Live orders always need your tap on Confirm buttons.\n\n"
        "Try: status · quote · paste a Kalshi/Polymarket link · /scout · /briefs"
    )


def link_detected(url: str) -> str:
    return f"Link detected:\n{url}\n\nAnalyzing with Scout…"


def trade_preview(preview: str, command: str) -> str:
    return (
        "Live trade preview\n\n"
        f"{preview}\n\n"
        f"Command:\n`{command}`\n\n"
        "Tap Review, then Execute YES to place the order."
    )


def trade_result(ok: bool, stdout: str, stderr: str) -> str:
    if ok:
        body = stdout or "Order submitted."
        return f"Trade OK\n\n{body}"
    body = stderr or stdout or "Unknown error"
    return f"Trade failed\n\n{body}"


def hermes_reply(text: str) -> str:
    if len(text) <= 3900:
        return text
    return text[:3900] + "\n\n…(truncated)"


def scenario_help() -> str:
    return (
        "Scenarios\n\n"
        "1. Quick quote — send: quote EVENT OUTCOME 1\n"
        "2. Poly quote — send: poly quote SLUG long\n"
        "3. Scout research — /scout your question or paste a market URL\n"
        "4. Brief flow — /briefs → Approve → /trader BRIEF.md\n"
        "5. Go live — /golive then /preflight (expect GO)\n"
        "6. Execute — Hermes gives ./pmx command → tap Queue trade"
    )
