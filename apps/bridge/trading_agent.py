"""
Trading agent capabilities — terminal-backed (Hermes/Grok safe).

Hermes cannot rely on PMXT MCP (Grok schema errors) or broken `./pmx poly markets`.
Agents use `./pmx link|quote|balance|positions` via this module or CLI:

    ./pmx agent snapshot
    ./pmx agent discover 'https://kalshi.com/markets/...'
    ./pmx agent portfolio
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Any

from apps.bridge.parse import (
    extract_trade_preview,
    parse_balance_json,
    parse_positions_json,
    parse_quote_fields,
    parse_rules_note,
    parse_status,
)
from apps.bridge.trade_safety import agent_doctor_json, credential_status, format_agent_doctor_report, sidecar_status
from apps.cockpit.bridge.pmx import ROOT, analyze_link, run_pmx

CAPABILITIES = (
    "market_discovery",
    "market_rules",
    "orderbook",
    "fair_value",
    "mispricing",
    "data_sources",
    "trade_recommendation",
    "confidence",
    "reasoning",
    "positions",
    "pnl",
    "exposure",
)


@dataclass
class CapabilityResult:
    capability: str
    ok: bool
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    command: str = ""


@dataclass
class TradeRecommendation:
    venue: str
    action: str
    outcome: str
    size: int
    limit_price: float | None
    fair_value_prob: float | None
    market_ask: float | None
    edge_pct: float | None
    confidence: float
    reasoning: str
    commands: list[str] = field(default_factory=list)


@dataclass
class PortfolioSnapshot:
    kill_switch: str
    kalshi_cash: str | None
    poly_cash: str | None
    kalshi_positions: list[dict[str, Any]]
    poly_positions: list[dict[str, Any]]
    open_count: int
    unrealized_pnl: float | None
    notional_exposure: float | None
    notes: list[str] = field(default_factory=list)


def discover_market(url: str, *, outcome: str = "USA", side: str = "long", size: float = 1) -> CapabilityResult:
    """Market discovery via link analyzer (Kalshi URL or Poly slug URL)."""
    r = analyze_link(url, outcome=outcome, side=side, size=size)
    stdout = r.get("stdout") or ""
    venue = r.get("venue") or "?"
    quote = parse_quote_fields(stdout)
    rules = parse_rules_note(stdout)
    ok = bool(r.get("ok")) and bool(quote or stdout.strip())
    summary = f"{venue} link ok" if ok else (r.get("error") or "discovery failed")
    return CapabilityResult(
        capability="market_discovery",
        ok=ok,
        summary=summary,
        command=r.get("command", ""),
        data={
            "url": url,
            "venue": venue,
            "quote": quote,
            "rules": rules,
            "preview": extract_trade_preview(stdout),
        },
    )


def read_orderbook(url: str, *, outcome: str = "USA", side: str = "long", size: float = 1) -> CapabilityResult:
    """Live price + top-of-book via ./pmx link (same subprocess as discovery)."""
    disc = discover_market(url, outcome=outcome, side=side, size=size)
    quote = disc.data.get("quote") or {}
    ok = disc.ok and bool(quote.get("best_bid") or quote.get("best_ask") or quote.get("mid"))
    return CapabilityResult(
        capability="orderbook",
        ok=ok,
        summary="book captured" if ok else "no bid/ask in link output",
        command=disc.command,
        data={"quote": quote, "preview": disc.data.get("preview", "")},
    )


def read_market_rules(url: str, **kwargs: Any) -> CapabilityResult:
    """Extract resolution/rules hints from link output; manual venue UI still authoritative."""
    disc = discover_market(url, **kwargs)
    rules = disc.data.get("rules") or {}
    text = rules.get("text") or ""
    ok = disc.ok
    summary = "rules snippet found" if text else "paste rules from venue UI into brief"
    return CapabilityResult(
        capability="market_rules",
        ok=ok,
        summary=summary,
        command=disc.command,
        data=rules,
    )


def estimate_fair_value(fair_prob: float, market_ask: float) -> CapabilityResult:
    """Fair value vs ask — edge per contract in probability points."""
    if not 0 <= fair_prob <= 1:
        return CapabilityResult("fair_value", False, "fair_prob must be 0–1", {})
    if market_ask <= 0:
        return CapabilityResult("fair_value", False, "market_ask must be > 0", {})
    edge = fair_prob - market_ask
    ev_per = edge  # $1 contract pays $1 at resolution
    return CapabilityResult(
        capability="fair_value",
        ok=True,
        summary=f"fair {fair_prob:.1%} vs ask {market_ask:.1%} → edge {edge:+.1%}",
        data={"fair_prob": fair_prob, "market_ask": market_ask, "edge_pct": edge, "ev_per_contract": ev_per},
    )


def detect_mispricing(
    fair_prob: float,
    market_ask: float,
    *,
    min_edge: float = 0.06,
    market_bid: float | None = None,
) -> CapabilityResult:
    """Flag +EV when fair value exceeds ask by min_edge."""
    fv = estimate_fair_value(fair_prob, market_ask)
    if not fv.ok:
        return CapabilityResult("mispricing", False, fv.summary, fv.data)
    edge = float(fv.data["edge_pct"])
    mispriced = edge >= min_edge
    sell_edge = None
    if market_bid is not None and market_bid > fair_prob + min_edge:
        sell_edge = market_bid - fair_prob
    return CapabilityResult(
        capability="mispricing",
        ok=True,
        summary="mispriced (buy)" if mispriced else "no buy edge at threshold",
        data={
            **fv.data,
            "min_edge": min_edge,
            "mispriced_buy": mispriced,
            "mispriced_sell": sell_edge is not None,
            "sell_edge_pct": sell_edge,
        },
    )


def check_data_sources(sources: list[str] | None = None) -> CapabilityResult:
    """Scout checklist — Hermes has no news API; agents cite external sources in brief."""
    default = [
        "Official venue rules page",
        "Primary data release (BLS, Fed, etc.)",
        "Cross-venue compare (./pmx compare url)",
        "Order book snapshot (./pmx link / quote)",
    ]
    items = sources or default
    return CapabilityResult(
        capability="data_sources",
        ok=True,
        summary=f"{len(items)} sources to verify in brief",
        data={"checklist": items, "note": "LLM must not invent prices — use ./pmx reads"},
    )


def score_confidence(
    *,
    book_liquid: bool = False,
    rules_clear: bool = False,
    data_fresh: bool = False,
    cross_venue_agrees: bool = False,
    edge_size: float = 0.0,
) -> CapabilityResult:
    """Heuristic 0–1 confidence from observable factors (not LLM self-report)."""
    score = 0.35
    if book_liquid:
        score += 0.15
    if rules_clear:
        score += 0.15
    if data_fresh:
        score += 0.1
    if cross_venue_agrees:
        score += 0.1
    if edge_size >= 0.08:
        score += 0.15
    elif edge_size >= 0.04:
        score += 0.08
    score = min(1.0, max(0.0, score))
    band = "high" if score >= 0.75 else ("medium" if score >= 0.55 else "low")
    return CapabilityResult(
        capability="confidence",
        ok=True,
        summary=f"confidence {score:.2f} ({band})",
        data={"score": round(score, 3), "band": band},
    )


def build_trade_recommendation(
    *,
    venue: str,
    action: str,
    outcome: str,
    size: int,
    fair_value_prob: float,
    market_ask: float,
    reasoning: str,
    slug_or_event: str,
    side: str = "long",
) -> TradeRecommendation:
    edge = fair_value_prob - market_ask
    conf = score_confidence(
        book_liquid=True,
        rules_clear=True,
        edge_size=max(0.0, edge),
    )
    if venue == "kalshi":
        cmds = [f"./pmx quote {slug_or_event} {outcome} {size}", f"./pmx trade {slug_or_event} {outcome} {size}"]
    else:
        cmds = [
            f"./pmx poly quote {slug_or_event} {side}",
            f"./pmx poly trade {slug_or_event} {side} {size}",
        ]
    return TradeRecommendation(
        venue=venue,
        action=action,
        outcome=outcome,
        size=size,
        limit_price=market_ask,
        fair_value_prob=fair_value_prob,
        market_ask=market_ask,
        edge_pct=edge,
        confidence=float(conf.data["score"]),
        reasoning=reasoning,
        commands=cmds,
    )


def fetch_portfolio(*, include_positions: bool = True) -> PortfolioSnapshot:
    """Balances + open positions across Kalshi and Poly US."""
    notes: list[str] = []
    status_r = run_pmx("status", timeout=45)
    status = parse_status(status_r.get("stdout") or "")

    kalshi_positions: list[dict[str, Any]] = []
    poly_positions: list[dict[str, Any]] = []

    if include_positions:
        with ThreadPoolExecutor(max_workers=4) as pool:
            fk = pool.submit(run_pmx, "balance", timeout=45)
            fp = pool.submit(run_pmx, "poly", "balance", timeout=45)
            fkp = pool.submit(run_pmx, "positions", timeout=60)
            fpp = pool.submit(run_pmx, "poly", "positions", timeout=60)
            k_bal = fk.result()
            p_bal = fp.result()
            k_pos = fkp.result()
            p_pos = fpp.result()
        k_avail, _ = parse_balance_json(k_bal.get("stdout") or "")
        p_avail, _ = parse_balance_json(p_bal.get("stdout") or "")
        if k_avail:
            status.kalshi_available = k_avail
        if p_avail:
            status.poly_available = p_avail
        kalshi_positions = parse_positions_json(k_pos.get("stdout") or "")
        poly_positions = parse_positions_json(p_pos.get("stdout") or "")
    else:
        k_avail = status.kalshi_available
        p_avail = status.poly_available

    all_pos = kalshi_positions + poly_positions
    unrealized = _sum_field(all_pos, "unrealized_pnl", "unrealizedPnL")
    notional = _sum_notional(all_pos)

    if not kalshi_positions and not poly_positions and include_positions:
        notes.append("No open positions or parse returned empty")

    return PortfolioSnapshot(
        kill_switch=status.kill_switch,
        kalshi_cash=status.kalshi_available,
        poly_cash=status.poly_available,
        kalshi_positions=kalshi_positions,
        poly_positions=poly_positions,
        open_count=len(all_pos),
        unrealized_pnl=unrealized,
        notional_exposure=notional,
        notes=notes,
    )


def agent_snapshot_json(*, probe_balances: bool = False) -> dict[str, Any]:
    """Full capability snapshot for Hermes / scripts."""
    portfolio = fetch_portfolio()
    sources = check_data_sources()
    return {
        "capabilities": list(CAPABILITIES),
        "hermes_notes": [
            "Use terminal ./pmx — PMXT MCP off by default on Grok",
            "Venue keys in pmxt/.env (NOT ~/.hermes/.env) — run ./pmx agent doctor if balance fails",
            "Read-only (PMX_READ_ONLY) blocks trades only — ./pmx balance still needs venue keys + warm sidecar",
            "./pmx poly markets often returns [] — use poly link/quote with known slugs",
            "Human confirms all live orders; ./pmx go-live required before trades",
        ],
        "credential_status": credential_status(ROOT),
        "sidecar_status": sidecar_status(ROOT, probe_balances=probe_balances),
        "portfolio": asdict(portfolio),
        "data_sources_checklist": sources.data.get("checklist", []),
    }


def _sum_field(rows: list[dict[str, Any]], *keys: str) -> float | None:
    total = 0.0
    found = False
    for row in rows:
        for key in keys:
            val = row.get(key)
            if val is None:
                continue
            try:
                total += float(val)
                found = True
            except (TypeError, ValueError):
                continue
    return total if found else None


def _sum_notional(rows: list[dict[str, Any]]) -> float | None:
    total = 0.0
    found = False
    for row in rows:
        size = row.get("size") or row.get("contracts") or row.get("shares")
        price = row.get("currentPrice") or row.get("current_price") or row.get("avgPrice")
        try:
            if size is not None and price is not None:
                total += abs(float(size) * float(price))
                found = True
            elif size is not None:
                total += abs(float(size))
                found = True
        except (TypeError, ValueError):
            continue
    return total if found else None


def _print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trading agent capabilities (terminal-backed)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("snapshot", help="Portfolio + capability manifest JSON")

    p_disc = sub.add_parser("discover", help="Discover market from URL")
    p_disc.add_argument("url")
    p_disc.add_argument("--outcome", default="USA")
    p_disc.add_argument("--side", default="long")
    p_disc.add_argument("--size", type=float, default=1.0)

    sub.add_parser("portfolio", help="Balances and positions JSON")

    p_doc = sub.add_parser("doctor", help="Credential + sidecar diagnostics (JSON or text)")
    p_doc.add_argument("--json", action="store_true", help="Emit JSON only")
    p_doc.add_argument("--probe", action="store_true", help="Probe live balance endpoints (default for doctor)")

    args = parser.parse_args(argv)
    if args.cmd == "snapshot":
        _print_json(agent_snapshot_json(probe_balances=False))
        return 0
    if args.cmd == "doctor":
        data = agent_doctor_json(ROOT, probe_balances=True)
        if args.json:
            _print_json(data)
        else:
            print(format_agent_doctor_report(data))
        creds = data.get("credential_status", {})
        sidecar = data.get("sidecar_status", {})
        if not creds.get("env_file_exists"):
            return 1
        if not sidecar.get("healthy"):
            return 1
        venues = sidecar.get("venues") or {}
        configured = [row for row in venues.values() if isinstance(row, dict) and row.get("configured")]
        if not configured:
            return 1
        return 0 if all(row.get("balance_ok") for row in configured) else 1
    if args.cmd == "portfolio":
        _print_json(asdict(fetch_portfolio()))
        return 0
    if args.cmd == "discover":
        disc = discover_market(args.url, outcome=args.outcome, side=args.side, size=args.size)
        rules = read_market_rules(args.url, outcome=args.outcome, side=args.side, size=args.size)
        book = read_orderbook(args.url, outcome=args.outcome, side=args.side, size=args.size)
        _print_json(
            {
                "discovery": asdict(disc),
                "rules": asdict(rules),
                "orderbook": asdict(book),
            }
        )
        return 0 if disc.ok else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
