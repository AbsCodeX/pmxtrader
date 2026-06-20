"""
Approval workflow — formatted proposal summary + explicit human YES.

Does not place orders. Outputs an approval packet for brief handoff.

CLI (via ``./pmx approve``):
    ./pmx approve --proposal proposal.json
    ./pmx approve --fair 0.62 --ask 0.50 --event EVENT
    ./pmx approve --proposal proposal.json --confirm YES --write
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apps.bridge.risk_engine import RiskCheck
from apps.bridge.trade_proposal import (
    TradeProposal,
    generate_proposal,
    proposal_from_url,
    proposal_to_dict,
)
from apps.bridge.trade_safety import confirm_trade_allowed

ROOT = Path(__file__).resolve().parents[2]


def _latest_proposal_json(root: Path) -> Path | None:
    candidates = sorted(
        (root / "briefs" / "active").glob("proposal-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def load_proposal_dict(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def proposal_from_dict(data: dict[str, Any]) -> TradeProposal:
    checks = [RiskCheck(**c) for c in data.get("risk_checks", [])]
    return TradeProposal(
        ok=bool(data.get("ok")),
        recommendation=str(data.get("recommendation", "PASS")),
        venue=str(data.get("venue", "kalshi")),
        market_ref=str(data.get("market_ref", "")),
        outcome=str(data.get("outcome", "YES")),
        fair_value_prob=float(data.get("fair_value_prob", 0)),
        market_ask=data.get("market_ask"),
        market_bid=data.get("market_bid"),
        edge_pct=data.get("edge_pct"),
        min_edge=float(data.get("min_edge", 0.06)),
        kelly_fraction=float(data.get("kelly_fraction", 0)),
        kelly_fraction_raw=float(data.get("kelly_fraction_raw", 0)),
        suggested_size=int(data.get("suggested_size", 0)),
        max_size_cap=int(data.get("max_size_cap", 10)),
        bankroll_used=data.get("bankroll_used"),
        max_risk_dollars=data.get("max_risk_dollars"),
        estimated_cost=data.get("estimated_cost"),
        confidence=float(data.get("confidence", 0)),
        confidence_band=str(data.get("confidence_band", "")),
        risk_checks=checks,
        passes_risk=bool(data.get("passes_risk")),
        reasoning=str(data.get("reasoning", "")),
        commands=list(data.get("commands", [])),
        brief_markdown=str(data.get("brief_markdown", "")),
    )


def format_approval_summary(proposal: TradeProposal) -> str:
    lines = [
        "=== Trade approval packet ===",
        "",
        f"Recommendation: {proposal.recommendation}",
        f"Venue: {proposal.venue}",
        f"Market: {proposal.market_ref}",
        f"Outcome: {proposal.outcome}",
        "",
        f"Fair value: {proposal.fair_value_prob:.1%}",
    ]
    if proposal.market_ask is not None:
        lines.append(f"Best ask: {proposal.market_ask:.1%}")
    if proposal.market_bid is not None:
        lines.append(f"Best bid: {proposal.market_bid:.1%}")
    if proposal.edge_pct is not None:
        lines.append(f"Edge: {proposal.edge_pct:+.1%}")
    lines.extend(
        [
            f"Kelly (scaled): {proposal.kelly_fraction:.1%}",
            f"Suggested size: {proposal.suggested_size} contracts",
            f"Est. cost: ${proposal.estimated_cost:.2f}" if proposal.estimated_cost else "Est. cost: —",
            f"Risk check: {'PASS' if proposal.passes_risk else 'REVIEW'}",
            "",
            f"Reasoning: {proposal.reasoning}",
            "",
            "Risk checks:",
        ]
    )
    for check in proposal.risk_checks:
        mark = "OK" if check.ok else "WARN"
        lines.append(f"  [{mark}] {check.name}: {check.detail}")
    if proposal.commands:
        lines.extend(["", "Commands (human runs after approval):"])
        for cmd in proposal.commands:
            lines.append(f"  {cmd}")
    lines.extend(
        [
            "",
            "Type YES to acknowledge approval packet (does not execute trades).",
        ]
    )
    return "\n".join(lines)


def wait_for_confirmation(*, confirm: str | None = None, interactive: bool = True) -> bool:
    if confirm is not None:
        return confirm_trade_allowed(confirm)
    if not interactive or not sys.stdin.isatty():
        return False
    try:
        answer = input("Confirm approval packet? Type YES: ").strip()
    except EOFError:
        return False
    return confirm_trade_allowed(answer)


def build_approval_packet(
    proposal: TradeProposal,
    *,
    confirmed: bool,
    source: str,
) -> dict[str, Any]:
    ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    return {
        "ok": proposal.ok and proposal.passes_risk,
        "confirmed": confirmed,
        "timestamp": ts,
        "source": source,
        "recommendation": proposal.recommendation,
        "venue": proposal.venue,
        "market_ref": proposal.market_ref,
        "outcome": proposal.outcome,
        "fair_value_prob": proposal.fair_value_prob,
        "edge_pct": proposal.edge_pct,
        "suggested_size": proposal.suggested_size,
        "estimated_cost": proposal.estimated_cost,
        "passes_risk": proposal.passes_risk,
        "commands": proposal.commands,
        "proposal": proposal_to_dict(proposal),
    }


def write_approval_packet(packet: dict[str, Any], *, root: Path | None = None) -> Path:
    root = root or ROOT
    out_dir = root / "briefs" / "active"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"approval-{packet['timestamp']}.json"
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    return path


def resolve_proposal(
    args: argparse.Namespace,
    *,
    root: Path,
) -> TradeProposal:
    if args.proposal:
        data = load_proposal_dict(Path(args.proposal))
        return proposal_from_dict(data)

    if args.latest:
        latest = _latest_proposal_json(root)
        if not latest:
            raise ValueError("No proposal-*.json found in briefs/active/")
        return proposal_from_dict(load_proposal_dict(latest))

    if args.url:
        return proposal_from_url(
            args.url,
            args.fair,
            outcome=args.outcome,
            side=args.side,
            min_edge=args.min_edge,
            kelly_scale=args.kelly_scale,
            bankroll=args.bankroll or 100.0,
            max_risk_dollars=args.max_risk,
            root=root,
        )

    if not args.market_ref:
        raise ValueError("Provide --proposal, --latest, --url, or --event/--slug")
    if args.ask is None and args.bid is None:
        raise ValueError("Provide --ask and/or --bid")
    return generate_proposal(
        fair_value_prob=args.fair,
        venue=args.venue,
        market_ref=args.market_ref,
        ask=args.ask,
        bid=args.bid,
        outcome=args.outcome,
        side=args.side,
        min_edge=args.min_edge,
        kelly_scale=args.kelly_scale,
        bankroll=args.bankroll or 100.0,
        max_risk_dollars=args.max_risk,
        root=root,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trade approval workflow (no execution)")
    parser.add_argument("--proposal", help="Path to proposal JSON from ./pmx propose")
    parser.add_argument("--latest", action="store_true", help="Use latest briefs/active/proposal-*.json")
    parser.add_argument("--fair", type=float, help="Fair value 0–1 (when building proposal)")
    parser.add_argument("--ask", type=float)
    parser.add_argument("--bid", type=float)
    parser.add_argument("--url")
    parser.add_argument("--venue", choices=("kalshi", "polymarket_us"), default="kalshi")
    parser.add_argument("--event", "--slug", dest="market_ref")
    parser.add_argument("--outcome", default="YES")
    parser.add_argument("--side", default="long")
    parser.add_argument("--min-edge", type=float, default=0.06)
    parser.add_argument("--kelly-scale", type=float, default=0.5)
    parser.add_argument("--bankroll", type=float)
    parser.add_argument("--max-risk", type=float)
    parser.add_argument("--confirm", help="Non-interactive YES confirmation")
    parser.add_argument("--write", action="store_true", help="Write briefs/active/approval-{ts}.json")
    parser.add_argument("--json", action="store_true", help="Output approval packet as JSON only")
    args = parser.parse_args(argv)

    root = ROOT
    if args.proposal is None and not args.latest and args.fair is None and args.url is None:
        print(
            json.dumps({"ok": False, "error": "Provide --proposal, --latest, --url, or --fair + market ref"}),
            file=sys.stderr,
        )
        return 1
    if args.fair is not None and not 0 <= args.fair <= 1:
        print(json.dumps({"ok": False, "error": "--fair must be 0–1"}), file=sys.stderr)
        return 1

    try:
        proposal = resolve_proposal(args, root=root)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    summary = format_approval_summary(proposal)
    if not args.json:
        print(summary)

    confirmed = wait_for_confirmation(confirm=args.confirm, interactive=args.confirm is None)
    source = args.proposal or ("latest" if args.latest else args.url or args.market_ref or "inline")
    packet = build_approval_packet(proposal, confirmed=confirmed, source=str(source))

    if args.write:
        path = write_approval_packet(packet, root=root)
        packet["written_to"] = str(path)

    if args.json:
        print(json.dumps(packet, indent=2))
    elif confirmed:
        print("\nApproval packet acknowledged.")
        if args.write:
            print(f"Written: {packet.get('written_to')}")
    else:
        print("\nNot confirmed — no approval recorded.", file=sys.stderr)
        return 1

    return 0 if packet["ok"] and confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
