"""Card-style messages — mirrors telegram/cards.ts."""

from __future__ import annotations


def _bold(text: str) -> str:
    return f"*{text}*"


def main_menu_message() -> str:
    return (
        "*pmxtrader*\n\n"
        "Choose a section below. Live trades always need Confirm — never one-tap execute.\n\n"
        "Paste a Kalshi or Polymarket URL · /menu anytime"
    )


def market_card(
    *,
    title: str,
    venue: str,
    outcome: str,
    price: str,
    volume: str = "",
    url: str = "",
    updated_at: str = "",
) -> str:
    lines = [
        _bold("Market"),
        title,
        f"Venue: {venue}",
        f"Outcome: {outcome}",
        f"Price: {price}",
    ]
    if volume:
        lines.append(f"Volume: {volume}")
    if updated_at:
        lines.append(f"Updated: {updated_at}")
    if url:
        lines.append(f"\n{url}")
    return "\n".join(lines)


def trade_confirm_card(
    *,
    venue: str,
    market: str,
    outcome: str,
    side: str,
    size: str,
    est_cost: str,
    command: str,
) -> str:
    return (
        f"{_bold('Trade confirmation')}\n"
        f"Venue: {venue}\n"
        f"Market: {market}\n"
        f"Outcome: {outcome}\n"
        f"Side: {side} · Size: {size}\n"
        f"Est. cost: {est_cost}\n\n"
        f"{_bold('Command')}\n"
        f"`{command}`\n\n"
        "Tap Confirm — never executes from a single button alone."
    )


def agent_status_card(
    *,
    mode: str,
    provider: str,
    kill_switch: str,
    read_only: str,
    session_id: str = "",
    last_action: str = "",
) -> str:
    lines = [
        _bold("Agent status"),
        f"Mode: {mode}",
        f"Provider: {provider}",
        f"Kill switch: {kill_switch}",
        f"Read-only: {read_only}",
    ]
    if session_id:
        lines.append(f"Session: {session_id[:8]}…")
    if last_action:
        lines.append(f"Last: {last_action}")
    return "\n".join(lines)


def alert_card(
    *,
    title: str,
    condition: str,
    market: str,
    status: str,
    triggered_at: str = "",
) -> str:
    lines = [
        _bold("Alert"),
        title,
        f"Condition: {condition}",
        f"Market: {market}",
        f"Status: {status}",
    ]
    if triggered_at:
        lines.append(f"Triggered: {triggered_at}")
    return "\n".join(lines)


def portfolio_card(
    *,
    kalshi_balance: str,
    poly_balance: str,
    open_positions: int,
    day_pnl: str = "",
    risk_note: str = "",
) -> str:
    lines = [
        _bold("Portfolio"),
        f"Kalshi: {kalshi_balance}",
        f"Polymarket US: {poly_balance}",
        f"Open positions: {open_positions}",
    ]
    if day_pnl:
        lines.append(f"Day P&L: {day_pnl}")
    if risk_note:
        lines.append(f"\n{risk_note}")
    return "\n".join(lines)


def loading_message(context: str) -> str:
    return f"Checking {context}…"


def error_message(context: str, detail: str) -> str:
    return f"{_bold('Error')} — {context}\n\n{detail}"


def help_card() -> str:
    return (
        f"{_bold('pmxtrader help')}\n"
        "Paste a Kalshi or Polymarket URL for Scout research.\n"
        "Use /menu anytime for inline buttons.\n\n"
        "Safety:\n"
        "• Live trades need Confirm + Execute (two taps)\n"
        "• Briefs need approved: true before Trader\n"
        "• ./pmx activate-live before real orders"
    )
