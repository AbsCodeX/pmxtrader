"""Trading safety guards for pmxtrader-owned live order paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TradeGuardResult:
    ok: bool
    error: str = ""


@dataclass(frozen=True)
class SafetySnapshot:
    kill_switch: str  # ON | OFF
    read_only: bool
    max_trade_contracts: float | None
    live_mode: bool
    kill_switch_reason: str | None = None


_DEFAULT_MAX_CONTRACTS = 10.0
_LIVE_MODE_FILE = ".pmx-live"


def max_trade_contracts() -> float | None:
    """Cap from PMX_MAX_TRADE_CONTRACTS (default 10 when unset in shell bootstrap)."""
    raw = os.environ.get("PMX_MAX_TRADE_CONTRACTS", "").strip()
    if not raw:
        return _DEFAULT_MAX_CONTRACTS
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if val > 0 else None


def live_mode_file(root: Path) -> Path:
    return root / _LIVE_MODE_FILE


def is_live_mode(root: Path) -> bool:
    return live_mode_file(root).is_file()


def is_read_only_env(*, root: Path | None = None) -> bool:
    if root is not None and is_live_mode(root):
        return False
    return os.environ.get("PMX_READ_ONLY", "1").strip().lower() in ("1", "true", "yes")


def trade_confirm_required(*, assume_yes: bool = False) -> bool:
    if assume_yes:
        return False
    return os.environ.get("PMX_TRADE_CONFIRM", "1").strip().lower() not in ("0", "false", "no")


def confirm_trade_allowed(answer: str) -> bool:
    return answer.strip() in ("YES", "y")


def read_kill_switch(root: Path) -> tuple[bool, str | None]:
    path = root / "KILL_SWITCH"
    if not path.is_file():
        return False, None
    try:
        reason = path.read_text(encoding="utf-8").splitlines()[0].strip()
    except OSError:
        reason = ""
    return True, reason or "engaged (no reason given)"


def safety_snapshot(root: Path) -> SafetySnapshot:
    engaged, reason = read_kill_switch(root)
    return SafetySnapshot(
        kill_switch="ON" if engaged else "OFF",
        read_only=is_read_only_env(root=root),
        max_trade_contracts=max_trade_contracts(),
        live_mode=is_live_mode(root),
        kill_switch_reason=reason if engaged else None,
    )


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


def check_live_trade_allowed(*, kill_switch_engaged: bool, root: Path | None = None) -> TradeGuardResult:
    if kill_switch_engaged:
        return TradeGuardResult(False, "Kill switch engaged — new trades blocked")
    if is_read_only_env(root=root):
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
