"""Trading safety guards for pmxtrader-owned live order paths."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TradeGuardResult:
    ok: bool
    error: str = ""


def max_trade_contracts() -> float | None:
    """Optional cap from PMX_MAX_TRADE_CONTRACTS (unset = no cap)."""
    raw = os.environ.get("PMX_MAX_TRADE_CONTRACTS", "").strip()
    if not raw:
        return None
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if val > 0 else None


def is_read_only_env() -> bool:
    return os.environ.get("PMX_READ_ONLY", "").strip().lower() in ("1", "true", "yes")


def check_trade_amount(amount: float | int | str) -> TradeGuardResult:
    try:
        qty = float(amount)
    except (TypeError, ValueError):
        return TradeGuardResult(False, f"Invalid trade size: {amount!r}")
    if qty <= 0:
        return TradeGuardResult(False, f"Trade size must be positive (got {qty:g})")
    cap = max_trade_contracts()
    if cap is not None and qty > cap:
        return TradeGuardResult(
            False,
            f"Trade size {qty:g} exceeds PMX_MAX_TRADE_CONTRACTS={cap:g}",
        )
    return TradeGuardResult(True)


def check_live_trade_allowed(*, kill_switch_engaged: bool) -> TradeGuardResult:
    if kill_switch_engaged:
        return TradeGuardResult(False, "Kill switch engaged — new trades blocked")
    if is_read_only_env():
        return TradeGuardResult(False, "READ-ONLY mode (PMX_READ_ONLY=1) — trades blocked")
    return TradeGuardResult(True)


def format_dry_run_order(
    *,
    venue: str,
    action: str,
    market: str,
    outcome: str,
    amount: float | int | str,
    order_type: str = "market",
    limit_price: str | None = None,
) -> str:
    base = f"[dry-run] {venue}: would {action} {amount} on {market} ({outcome})"
    if order_type == "limit" and limit_price:
        return f"{base} @ limit {limit_price}"
    return f"{base} @ {order_type}"
