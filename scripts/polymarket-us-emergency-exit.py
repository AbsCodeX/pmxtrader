#!/usr/bin/env python3
"""Cancel resting Polymarket US orders and optionally market-close open positions."""
from __future__ import annotations

import argparse
import json
import sys
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.bridge.dashboard_security import minimal_subprocess_env  # noqa: E402
from apps.bridge.pmxt_cli import pmxt_argv  # noqa: E402

EXCHANGE = "polymarket_us"
REQUEST_INTERVAL_SEC = 0.1


def pmxt_json(args: list[str]) -> Any:
    import subprocess

    argv = pmxt_argv([*args, "--json"], root=ROOT)
    subprocess_env = minimal_subprocess_env(ROOT)
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
        env=subprocess_env,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(err or f"pmxt failed: {' '.join(args)}")
    return json.loads(result.stdout)


def cancel_open_orders(*, dry_run: bool) -> list[dict[str, Any]]:
    orders = pmxt_json(["orders:open", "--exchange", EXCHANGE, "--local"])
    if not isinstance(orders, list):
        orders = []
    results: list[dict[str, Any]] = []
    for order in orders:
        order_id = order.get("id")
        if not order_id:
            continue
        entry = {
            "orderId": order_id,
            "marketId": order.get("marketId"),
            "status": "dry_run" if dry_run else "pending",
        }
        if dry_run:
            results.append(entry)
            continue
        try:
            pmxt_json(["order:cancel", str(order_id), "--exchange", EXCHANGE, "--local"])
            entry["status"] = "canceled"
        except RuntimeError as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
        results.append(entry)
        time.sleep(REQUEST_INTERVAL_SEC)
    return results


def _position_size(raw: dict[str, Any]) -> Decimal:
    size = raw.get("size")
    if size is None:
        return Decimal(0)
    return Decimal(str(size))


def close_positions(*, dry_run: bool) -> list[dict[str, Any]]:
    positions = pmxt_json([EXCHANGE, "positions", "--local"])
    if not isinstance(positions, list):
        positions = []
    results: list[dict[str, Any]] = []
    for pos in positions:
        size = _position_size(pos)
        if size <= 0:
            continue
        market_id = pos.get("marketId") or ""
        outcome_id = pos.get("outcomeId") or ""
        entry = {
            "marketId": market_id,
            "outcomeId": outcome_id,
            "size": str(size),
            "status": "dry_run" if dry_run else "pending",
        }
        if dry_run:
            entry["action"] = "market sell"
            results.append(entry)
            continue
        try:
            qty = int(size) if size == int(size) else size
            resp = pmxt_json(
                [
                    "order:create",
                    "--exchange",
                    EXCHANGE,
                    "--market-id",
                    str(market_id),
                    "--outcome-id",
                    str(outcome_id),
                    "--side",
                    "sell",
                    "--type",
                    "market",
                    "--amount",
                    str(qty),
                    "--local",
                ]
            )
            entry["status"] = "submitted"
            if isinstance(resp, list) and resp:
                entry["orderId"] = resp[0].get("id")
            elif isinstance(resp, dict):
                entry["orderId"] = resp.get("id")
        except (RuntimeError, ValueError, InvalidOperation) as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
        results.append(entry)
        time.sleep(REQUEST_INTERVAL_SEC)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Polymarket US emergency cancel / cash-out")
    parser.add_argument("--cancel-orders", action="store_true")
    parser.add_argument("--close-positions", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.cancel_orders and not args.close_positions:
        parser.error("Specify --cancel-orders and/or --close-positions")

    report: dict[str, Any] = {"cancelOrders": [], "closePositions": []}
    try:
        if args.cancel_orders:
            report["cancelOrders"] = cancel_open_orders(dry_run=args.dry_run)
        if args.close_positions:
            report["closePositions"] = close_positions(dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if report["cancelOrders"]:
            print("=== Cancel Polymarket US resting orders ===")
            for row in report["cancelOrders"]:
                print(f"  {row.get('orderId')} {row.get('marketId')} -> {row.get('status')}")
        if report["closePositions"]:
            print("=== Close Polymarket US positions (market sell) ===")
            for row in report["closePositions"]:
                extra = f" order={row.get('orderId')}" if row.get("orderId") else ""
                err = f" ({row.get('error')})" if row.get("error") else ""
                print(
                    f"  {row.get('marketId')} {row.get('outcomeId')} "
                    f"size={row.get('size')} -> {row.get('status')}{extra}{err}"
                )

    errors = [
        *[
            r
            for r in report.get("cancelOrders", [])
            if r.get("status") == "error"
        ],
        *[
            r
            for r in report.get("closePositions", [])
            if r.get("status") == "error"
        ],
    ]
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
