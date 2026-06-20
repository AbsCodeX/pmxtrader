"""
Risk & sizing engine — edge, Kelly, position caps, daily loss ledger.

CLI (via ``./pmx risk``):
    ./pmx risk check --fair F --ask A [--bankroll B]
    ./pmx risk status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from math import floor
from pathlib import Path

from apps.bridge.trade_safety import (
    check_live_trade_allowed,
    check_trade_amount,
    max_trade_contracts,
    read_kill_switch,
)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class RiskCheck:
    name: str
    ok: bool
    detail: str


@dataclass
class RiskReport:
    ok: bool
    checks: list[RiskCheck] = field(default_factory=list)
    edge: float | None = None
    kelly_fraction: float = 0.0
    kelly_fraction_raw: float = 0.0
    suggested_size: int = 0
    estimated_cost: float | None = None


def compute_edge(
    fair: float,
    *,
    ask: float | None = None,
    bid: float | None = None,
    side: str = "buy",
) -> float | None:
    """Edge for buy-YES (fair − ask) or buy-NO / fade-YES (bid − fair or NO edge)."""
    side_l = side.lower()
    if side_l in ("buy", "yes"):
        return (fair - ask) if ask is not None else None
    if side_l in ("sell", "no"):
        if bid is not None:
            return bid - fair
        if ask is not None:
            no_ask = 1.0 - ask
            return (1.0 - fair) - no_ask
    return None


def kelly_fraction_yes(fair: float, ask: float) -> float:
    """Full Kelly fraction of bankroll for buying YES at ``ask``."""
    if ask <= 0 or ask >= 1 or fair <= ask:
        return 0.0
    return max(0.0, (fair - ask) / (1.0 - ask))


def kelly_fraction_no(fair: float, no_ask: float) -> float:
    """Full Kelly fraction of bankroll for buying NO at ``no_ask``."""
    fair_no = 1.0 - fair
    if no_ask <= 0 or no_ask >= 1 or fair_no <= no_ask:
        return 0.0
    return max(0.0, (fair_no - no_ask) / (1.0 - no_ask))


def size_from_kelly(
    *,
    kelly_fraction: float,
    bankroll: float,
    price_per_contract: float,
    max_contracts: int,
) -> tuple[int, float | None]:
    """Kelly contracts capped by max_contracts and bankroll."""
    if price_per_contract <= 0 or bankroll <= 0 or kelly_fraction <= 0:
        return 0, None
    raw = kelly_fraction * bankroll / price_per_contract
    size = int(floor(raw))
    size = max(0, min(size, max_contracts))
    cost = round(size * price_per_contract, 2) if size else None
    return size, cost


def kelly_size(
    fair: float,
    *,
    ask: float | None = None,
    bid: float | None = None,
    side: str = "buy",
    bankroll: float,
    kelly_scale: float = 0.5,
    max_contracts: int | None = None,
) -> dict[str, float | int | None]:
    """Return Kelly sizing dict (fraction, size, cost)."""
    cap = int(max_contracts if max_contracts is not None else (max_trade_contracts() or 10))
    side_l = side.lower()
    raw = 0.0
    price: float | None = None
    if side_l in ("buy", "yes") and ask is not None:
        raw = kelly_fraction_yes(fair, ask)
        price = ask
    elif side_l in ("sell", "no"):
        if bid is not None:
            no_ask = round(1.0 - bid, 4)
            raw = kelly_fraction_no(fair, no_ask)
            price = no_ask
        elif ask is not None:
            no_ask = 1.0 - ask
            raw = kelly_fraction_no(fair, no_ask)
            price = no_ask
    scaled = raw * kelly_scale
    size, cost = size_from_kelly(
        kelly_fraction=scaled,
        bankroll=bankroll,
        price_per_contract=price or 0.0,
        max_contracts=cap,
    )
    return {
        "kelly_fraction_raw": raw,
        "kelly_fraction": scaled,
        "suggested_size": size,
        "estimated_cost": cost,
        "max_contracts": cap,
        "price_per_contract": price,
    }


def max_daily_loss() -> float | None:
    """Max daily loss $ from PMX_MAX_DAILY_LOSS (unset → guard inactive)."""
    raw = os.environ.get("PMX_MAX_DAILY_LOSS", "").strip()
    if not raw:
        return None
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if val > 0 else None


def max_portfolio_pct() -> float | None:
    """Max portfolio % per trade from PMX_MAX_PORTFOLIO_PCT."""
    raw = os.environ.get("PMX_MAX_PORTFOLIO_PCT", "").strip()
    if not raw:
        return None
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if 0 < val <= 1 else None


def daily_ledger_path(root: Path | None = None) -> Path:
    return (root or ROOT) / "briefs" / "ledger" / "daily.json"


def _today() -> str:
    return date.today().isoformat()


def _empty_ledger() -> dict:
    return {"date": _today(), "realized_pnl": 0.0, "trades": []}


def load_daily_ledger(root: Path | None = None) -> dict:
    path = daily_ledger_path(root)
    if not path.is_file():
        return _empty_ledger()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_ledger()
    if not isinstance(data, dict) or data.get("date") != _today():
        return _empty_ledger()
    data.setdefault("realized_pnl", 0.0)
    data.setdefault("trades", [])
    return data


def save_daily_ledger(data: dict, root: Path | None = None) -> Path:
    path = daily_ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def record_trade_pnl(pnl: float, *, root: Path | None = None, note: str = "") -> dict:
    """Append realized P&L to today's ledger."""
    ledger = load_daily_ledger(root)
    ledger["realized_pnl"] = round(float(ledger.get("realized_pnl", 0)) + pnl, 2)
    trades = ledger.setdefault("trades", [])
    trades.append(
        {
            "ts": datetime.now(tz=UTC).isoformat(),
            "pnl": round(pnl, 2),
            "note": note,
        }
    )
    save_daily_ledger(ledger, root)
    return ledger


def daily_loss_status(root: Path | None = None) -> dict:
    """Daily loss guard status (blocked until PMX_MAX_DAILY_LOSS is set)."""
    limit = max_daily_loss()
    ledger = load_daily_ledger(root)
    pnl = float(ledger.get("realized_pnl", 0))
    if limit is None:
        return {
            "ok": False,
            "blocked": True,
            "reason": "PMX_MAX_DAILY_LOSS not set — daily loss guard disabled until configured",
            "realized_pnl": pnl,
            "limit": None,
            "remaining": None,
            "date": ledger.get("date", _today()),
        }
    blocked = pnl <= -limit
    remaining = round(limit + pnl, 2)
    return {
        "ok": not blocked,
        "blocked": blocked,
        "reason": (
            f"Daily loss ${abs(pnl):.2f} exceeds limit ${limit:.2f}"
            if blocked
            else f"Within daily loss limit (${remaining:.2f} headroom)"
        ),
        "realized_pnl": pnl,
        "limit": limit,
        "remaining": remaining,
        "date": ledger.get("date", _today()),
    }


def check_risk(
    *,
    size: int,
    recommendation: str = "YES",
    venue: str = "kalshi",
    root: Path | None = None,
    max_risk_dollars: float | None = None,
    estimated_cost: float | None = None,
    bankroll: float | None = None,
    fair: float | None = None,
    ask: float | None = None,
    bid: float | None = None,
) -> RiskReport:
    """Run safety + sizing risk checks."""
    root = root or ROOT
    checks: list[RiskCheck] = []
    edge = compute_edge(fair, ask=ask, bid=bid, side="buy") if fair is not None else None

    engaged, reason = read_kill_switch(root)
    checks.append(
        RiskCheck(
            "kill_switch",
            not engaged,
            "OFF" if not engaged else f"ON — {reason or 'engaged'}",
        )
    )
    live = check_live_trade_allowed(kill_switch_engaged=engaged, root=root)
    checks.append(
        RiskCheck(
            "read_only",
            live.ok or "READ-ONLY" not in live.error,
            "proposal only" if not live.ok else "live trading allowed",
        )
    )

    if recommendation == "PASS":
        checks.append(RiskCheck("edge_threshold", False, "PASS — no +EV side at min edge"))
    else:
        checks.append(RiskCheck("edge_threshold", True, f"{recommendation} meets min edge"))

    if size > 0:
        amt = check_trade_amount(size)
        cap = max_trade_contracts()
        checks.append(
            RiskCheck(
                "max_contracts",
                amt.ok,
                f"{size} contracts (cap {cap:g})" if amt.ok else amt.error,
            )
        )
    else:
        checks.append(RiskCheck("kelly_size", False, "Kelly size is 0 — skip or raise bankroll"))

    if max_risk_dollars is not None and estimated_cost is not None:
        under = estimated_cost <= max_risk_dollars
        checks.append(
            RiskCheck(
                "max_risk_dollars",
                under,
                f"${estimated_cost:.2f} vs max ${max_risk_dollars:.2f}",
            )
        )

    pct = max_portfolio_pct()
    if pct is not None and estimated_cost is not None and bankroll is not None and bankroll > 0:
        pct_used = estimated_cost / bankroll
        under = pct_used <= pct
        checks.append(
            RiskCheck(
                "max_portfolio_pct",
                under,
                f"{pct_used:.1%} of bankroll vs cap {pct:.1%}",
            )
        )

    dl = daily_loss_status(root)
    checks.append(
        RiskCheck(
            "daily_loss",
            dl["ok"] and not dl["blocked"],
            dl["reason"],
        )
    )

    if venue == "kalshi":
        checks.append(
            RiskCheck("venue_keys", True, "verify KALSHI keys in pmxt/.env before live trade")
        )
    elif venue == "polymarket_us":
        checks.append(
            RiskCheck("venue_keys", True, "verify POLYMARKET_US keys in pmxt/.env before live trade")
        )

    blocking_names = ("max_contracts", "max_risk_dollars", "kelly_size", "daily_loss", "max_portfolio_pct")
    blocking = [c for c in checks if c.name in blocking_names]
    passes = recommendation != "PASS" and size > 0 and all(c.ok for c in blocking)
    return RiskReport(ok=passes, checks=checks, edge=edge, suggested_size=size, estimated_cost=estimated_cost)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Risk & sizing engine")
    sub = parser.add_subparsers(dest="command", required=True)

    check_p = sub.add_parser("check", help="Edge + Kelly + risk checks")
    check_p.add_argument("--fair", type=float, required=True)
    check_p.add_argument("--ask", type=float)
    check_p.add_argument("--bid", type=float)
    check_p.add_argument("--bankroll", type=float, default=100.0)
    check_p.add_argument("--kelly-scale", type=float, default=0.5)
    check_p.add_argument("--max-risk", type=float)
    check_p.add_argument("--venue", default="kalshi")

    sub.add_parser("status", help="Daily loss ledger status")

    args = parser.parse_args(argv)
    root = ROOT

    if args.command == "status":
        print(json.dumps(daily_loss_status(root), indent=2))
        return 0

    if not 0 <= args.fair <= 1:
        print(json.dumps({"ok": False, "error": "--fair must be 0–1"}), file=sys.stderr)
        return 1
    if args.ask is None and args.bid is None:
        print(json.dumps({"ok": False, "error": "Provide --ask and/or --bid"}), file=sys.stderr)
        return 1

    edge = compute_edge(args.fair, ask=args.ask, bid=args.bid, side="buy")
    side = "buy"
    if edge is not None and edge < 0 and args.bid is not None:
        edge = compute_edge(args.fair, bid=args.bid, side="no")
        side = "no"

    sizing = kelly_size(
        args.fair,
        ask=args.ask,
        bid=args.bid,
        side=side,
        bankroll=args.bankroll,
        kelly_scale=args.kelly_scale,
    )
    report = check_risk(
        size=int(sizing["suggested_size"]),
        recommendation="YES" if (edge or 0) > 0 else "PASS",
        venue=args.venue,
        root=root,
        max_risk_dollars=args.max_risk,
        estimated_cost=sizing["estimated_cost"],  # type: ignore[arg-type]
        bankroll=args.bankroll,
        fair=args.fair,
        ask=args.ask,
        bid=args.bid,
    )
    report.kelly_fraction = float(sizing["kelly_fraction"] or 0)
    report.kelly_fraction_raw = float(sizing["kelly_fraction_raw"] or 0)
    report.edge = edge

    out = {
        "ok": report.ok,
        "edge": edge,
        "kelly_fraction": report.kelly_fraction,
        "kelly_fraction_raw": report.kelly_fraction_raw,
        "suggested_size": report.suggested_size,
        "estimated_cost": report.estimated_cost,
        "checks": [asdict(c) for c in report.checks],
        "daily_loss": daily_loss_status(root),
    }
    print(json.dumps(out, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
