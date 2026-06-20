"""
Trade proposal generator — market + edge → formatted approval packet.

Combines fair-value edge, Kelly sizing, safety checks, and Yes/No/PASS
recommendation for Scout → Human approval workflow.

CLI:
    ./pmx propose --fair 0.62 --ask 0.50 --venue kalshi --event EVENT --outcome YES
    ./pmx propose --url URL --fair 0.62 [--markdown]
    ./pmx agent propose ...  (same)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from apps.bridge.risk_engine import (
    RiskCheck,
    kelly_fraction_no,
    kelly_fraction_yes,
    size_from_kelly,
)
from apps.bridge.trade_safety import max_trade_contracts
from apps.bridge.trading_agent import (
    build_trade_recommendation,
    detect_mispricing,
    discover_market,
    estimate_fair_value,
    fetch_portfolio,
    score_confidence,
)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class TradeProposal:
    ok: bool
    recommendation: str  # YES | NO | PASS
    venue: str
    market_ref: str
    outcome: str
    fair_value_prob: float
    market_ask: float | None
    market_bid: float | None
    edge_pct: float | None
    min_edge: float
    kelly_fraction: float
    kelly_fraction_raw: float
    suggested_size: int
    max_size_cap: int
    bankroll_used: float | None
    max_risk_dollars: float | None
    estimated_cost: float | None
    confidence: float
    confidence_band: str
    risk_checks: list[RiskCheck] = field(default_factory=list)
    passes_risk: bool = False
    reasoning: str = ""
    commands: list[str] = field(default_factory=list)
    brief_markdown: str = ""


def pick_recommendation(
    fair: float,
    *,
    ask: float | None,
    bid: float | None,
    min_edge: float,
) -> tuple[str, float | None, str]:
    """Return (YES|NO|PASS, edge, reasoning snippet)."""
    buy_edge = (fair - ask) if ask is not None else None
    sell_edge = (bid - fair) if bid is not None else None

    if buy_edge is not None and buy_edge >= min_edge:
        return (
            "YES",
            buy_edge,
            f"Fair {fair:.1%} vs ask {ask:.1%} → edge {buy_edge:+.1%} (buy YES)",
        )
    if sell_edge is not None and sell_edge >= min_edge:
        return (
            "NO",
            sell_edge,
            f"Fair {fair:.1%} vs bid {bid:.1%} → edge {sell_edge:+.1%} (buy NO / fade YES)",
        )

    best = buy_edge if buy_edge is not None else sell_edge
    if buy_edge is not None and sell_edge is not None:
        if abs(sell_edge) > abs(buy_edge):
            best = sell_edge
        else:
            best = buy_edge
    detail = ""
    if ask is not None:
        detail = f"ask edge {buy_edge:+.1%}" if buy_edge is not None else ""
    if bid is not None:
        bid_part = f"bid edge {sell_edge:+.1%}" if sell_edge is not None else ""
        detail = f"{detail}; {bid_part}" if detail else bid_part
    return (
        "PASS",
        best,
        f"No trade: {detail or 'insufficient book'} (min edge {min_edge:.1%})",
    )


def run_risk_checks(
    *,
    size: int,
    recommendation: str,
    venue: str,
    root: Path,
    max_risk_dollars: float | None,
    estimated_cost: float | None,
    bankroll: float | None = None,
    fair: float | None = None,
    ask: float | None = None,
    bid: float | None = None,
) -> tuple[list[RiskCheck], bool]:
    from apps.bridge.risk_engine import check_risk

    report = check_risk(
        size=size,
        recommendation=recommendation,
        venue=venue,
        root=root,
        max_risk_dollars=max_risk_dollars,
        estimated_cost=estimated_cost,
        bankroll=bankroll,
        fair=fair,
        ask=ask,
        bid=bid,
    )
    return report.checks, report.ok


def format_brief_markdown(proposal: TradeProposal, *, title: str = "Trade proposal") -> str:
    lines = [
        f"## {title}",
        "",
        f"- **Recommendation:** **{proposal.recommendation}**",
        f"- **Venue:** {proposal.venue}",
        f"- **Market:** {proposal.market_ref}",
        f"- **Outcome / side:** {proposal.outcome}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Fair value | {proposal.fair_value_prob:.1%} |",
    ]
    if proposal.market_ask is not None:
        lines.append(f"| Best ask | {proposal.market_ask:.1%} |")
    if proposal.market_bid is not None:
        lines.append(f"| Best bid | {proposal.market_bid:.1%} |")
    if proposal.edge_pct is not None:
        lines.append(f"| Edge | {proposal.edge_pct:+.1%} |")
    lines.extend(
        [
            f"| Kelly (half) | {proposal.kelly_fraction:.1%} of bankroll |",
            f"| Suggested size | {proposal.suggested_size} contracts |",
            f"| Est. cost | ${proposal.estimated_cost:.2f} |"
            if proposal.estimated_cost is not None
            else "| Est. cost | — |",
            f"| Confidence | {proposal.confidence:.2f} ({proposal.confidence_band}) |",
            f"| Risk check | {'PASS' if proposal.passes_risk else 'REVIEW'} |",
            "",
            f"**Reasoning:** {proposal.reasoning}",
            "",
            "**Commands (human confirms before run):**",
            "",
        ]
    )
    for cmd in proposal.commands:
        lines.append(f"```bash\n{cmd}\n```")
        lines.append("")
    lines.append("**Risk checks:**")
    for check in proposal.risk_checks:
        mark = "OK" if check.ok else "WARN"
        lines.append(f"- [{mark}] {check.name}: {check.detail}")
    return "\n".join(lines)


def generate_proposal(
    *,
    fair_value_prob: float,
    venue: str,
    market_ref: str,
    ask: float | None = None,
    bid: float | None = None,
    outcome: str = "YES",
    side: str = "long",
    min_edge: float = 0.06,
    kelly_scale: float = 0.5,
    bankroll: float | None = None,
    max_risk_dollars: float | None = None,
    max_contracts: int | None = None,
    reasoning: str = "",
    root: Path | None = None,
) -> TradeProposal:
    """Build a full trade proposal from fair value and market prices."""
    root = root or ROOT
    cap = int(max_contracts if max_contracts is not None else (max_trade_contracts() or 10))

    recommendation, edge, reason = pick_recommendation(
        fair_value_prob, ask=ask, bid=bid, min_edge=min_edge
    )
    if not reasoning:
        reasoning = reason

    raw_kelly = 0.0
    price = ask
    trade_outcome = outcome
    if recommendation == "YES" and ask is not None:
        raw_kelly = kelly_fraction_yes(fair_value_prob, ask)
        price = ask
        trade_outcome = outcome if venue == "kalshi" else side
    elif recommendation == "NO":
        if bid is not None:
            no_ask = round(1.0 - bid, 4)
            raw_kelly = kelly_fraction_no(fair_value_prob, no_ask)
            price = no_ask
            trade_outcome = "NO" if venue == "kalshi" else "short"
        elif ask is not None:
            raw_kelly = kelly_fraction_no(fair_value_prob, 1.0 - ask)
            price = 1.0 - ask
            trade_outcome = "NO" if venue == "kalshi" else "short"

    kelly = raw_kelly * kelly_scale
    br = bankroll
    size = 0
    cost: float | None = None
    if br is not None and price is not None and price > 0:
        size, cost = size_from_kelly(
            kelly_fraction=kelly,
            bankroll=br,
            price_per_contract=price,
            max_contracts=cap,
        )
    elif recommendation != "PASS" and price is not None:
        size = min(1, cap)
        cost = round(size * price, 2)

    checks, passes = run_risk_checks(
        size=size,
        recommendation=recommendation,
        venue=venue,
        root=root,
        max_risk_dollars=max_risk_dollars,
        estimated_cost=cost,
        bankroll=br,
        fair=fair_value_prob,
        ask=ask,
        bid=bid,
    )

    conf = score_confidence(
        book_liquid=ask is not None and bid is not None,
        rules_clear=True,
        edge_size=max(0.0, edge or 0.0),
    )

    mis = detect_mispricing(fair_value_prob, ask or 1.0, min_edge=min_edge, market_bid=bid)
    rec = build_trade_recommendation(
        venue=venue,
        action="buy" if recommendation != "PASS" else "hold",
        outcome=trade_outcome,
        size=size if size > 0 else 1,
        fair_value_prob=fair_value_prob,
        market_ask=ask or 0.0,
        reasoning=reasoning,
        slug_or_event=market_ref,
        side=side,
    )
    commands = rec.commands if recommendation != "PASS" and size > 0 else []
    proposal = TradeProposal(
        ok=recommendation != "PASS",
        recommendation=recommendation,
        venue=venue,
        market_ref=market_ref,
        outcome=trade_outcome,
        fair_value_prob=fair_value_prob,
        market_ask=ask,
        market_bid=bid,
        edge_pct=edge,
        min_edge=min_edge,
        kelly_fraction=kelly,
        kelly_fraction_raw=raw_kelly,
        suggested_size=size,
        max_size_cap=cap,
        bankroll_used=br,
        max_risk_dollars=max_risk_dollars,
        estimated_cost=cost,
        confidence=float(conf.data["score"]),
        confidence_band=str(conf.data["band"]),
        risk_checks=checks,
        passes_risk=passes,
        reasoning=reasoning,
        commands=commands,
    )
    proposal.brief_markdown = format_brief_markdown(proposal)
    _ = mis  # mispricing already reflected in recommendation
    return proposal


def proposal_from_url(
    url: str,
    fair_value_prob: float,
    *,
    outcome: str = "USA",
    side: str = "long",
    **kwargs: Any,
) -> TradeProposal:
    disc = discover_market(url, outcome=outcome, side=side)
    quote = disc.data.get("quote") or {}
    venue = disc.data.get("venue") or "kalshi"
    if venue not in ("kalshi", "polymarket_us", "polymarket"):
        venue = "kalshi" if "kalshi" in url else "polymarket_us"
    if venue == "polymarket":
        venue = "polymarket_us"
    market_ref = (
        quote.get("event_id")
        or quote.get("slug")
        or disc.data.get("url", url)
    )
    return generate_proposal(
        fair_value_prob=fair_value_prob,
        venue=venue,
        market_ref=str(market_ref),
        ask=_float_or_none(quote.get("best_ask")),
        bid=_float_or_none(quote.get("best_bid")),
        outcome=outcome,
        side=side,
        reasoning=kwargs.pop("reasoning", "") or f"Discovery via {url}",
        **kwargs,
    )


def _float_or_none(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _parse_bankroll(raw: str | None, *, use_portfolio: bool) -> float | None:
    if raw is not None:
        try:
            return float(raw)
        except ValueError:
            return None
    if not use_portfolio:
        return None
    port = fetch_portfolio(include_positions=False)
    cash = port.kalshi_cash or port.poly_cash
    if cash is None:
        return None
    try:
        return float(str(cash).replace("$", "").replace(",", ""))
    except ValueError:
        return None


def proposal_to_dict(proposal: TradeProposal) -> dict[str, Any]:
    data = asdict(proposal)
    data["risk_checks"] = [asdict(c) for c in proposal.risk_checks]
    if proposal.market_ask is not None and proposal.market_ask > 0:
        data["fair_value"] = asdict(
            estimate_fair_value(proposal.fair_value_prob, proposal.market_ask)
        )
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate formatted trade proposal")
    parser.add_argument("--fair", type=float, required=True, help="Fair value probability 0–1")
    parser.add_argument("--ask", type=float, help="Best ask (decimal 0–1)")
    parser.add_argument("--bid", type=float, help="Best bid (decimal 0–1)")
    parser.add_argument("--url", help="Market URL — fetch bid/ask via ./pmx link")
    parser.add_argument("--venue", choices=("kalshi", "polymarket_us"), default="kalshi")
    parser.add_argument("--event", "--slug", dest="market_ref", help="Event ID or slug")
    parser.add_argument("--outcome", default="YES", help="Kalshi outcome label")
    parser.add_argument("--side", default="long", help="Poly US side (long/short)")
    parser.add_argument("--min-edge", type=float, default=0.06)
    parser.add_argument("--kelly-scale", type=float, default=0.5, help="Half-Kelly default 0.5")
    parser.add_argument("--bankroll", type=float, help="Bankroll $ for Kelly sizing")
    parser.add_argument(
        "--use-portfolio",
        action="store_true",
        help="Use available cash from ./pmx agent portfolio",
    )
    parser.add_argument("--max-risk", type=float, help="Max dollars at risk for this trade")
    parser.add_argument("--max-contracts", type=int)
    parser.add_argument("--reason", default="")
    parser.add_argument("--markdown", action="store_true", help="Print brief markdown section")
    args = parser.parse_args(argv)

    if not 0 <= args.fair <= 1:
        print(json.dumps({"ok": False, "error": "--fair must be between 0 and 1"}), file=sys.stderr)
        return 1

    bankroll = _parse_bankroll(
        str(args.bankroll) if args.bankroll is not None else None,
        use_portfolio=args.use_portfolio,
    )
    if args.bankroll is None and not args.use_portfolio:
        bankroll = bankroll or 100.0  # default sizing reference for proposals

    if args.url:
        proposal = proposal_from_url(
            args.url,
            args.fair,
            outcome=args.outcome,
            side=args.side,
            min_edge=args.min_edge,
            kelly_scale=args.kelly_scale,
            bankroll=bankroll,
            max_risk_dollars=args.max_risk,
            max_contracts=args.max_contracts,
            reasoning=args.reason,
        )
    else:
        if not args.market_ref:
            print(
                json.dumps({"ok": False, "error": "Provide --event/--slug or --url"}),
                file=sys.stderr,
            )
            return 1
        if args.ask is None and args.bid is None:
            print(
                json.dumps({"ok": False, "error": "Provide --ask and/or --bid (or --url)"}),
                file=sys.stderr,
            )
            return 1
        proposal = generate_proposal(
            fair_value_prob=args.fair,
            venue=args.venue,
            market_ref=args.market_ref,
            ask=args.ask,
            bid=args.bid,
            outcome=args.outcome,
            side=args.side,
            min_edge=args.min_edge,
            kelly_scale=args.kelly_scale,
            bankroll=bankroll,
            max_risk_dollars=args.max_risk,
            max_contracts=args.max_contracts,
            reasoning=args.reason,
        )

    if args.markdown:
        print(proposal.brief_markdown)
    else:
        print(json.dumps(proposal_to_dict(proposal), indent=2))
    return 0 if proposal.ok else 1


if __name__ == "__main__":
    sys.exit(main())
