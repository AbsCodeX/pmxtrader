#!/usr/bin/env python3
"""Cancel resting Kalshi orders and optionally market-close open positions.

Uses Kalshi REST directly for position closes so action/side are correct
(PMXT createOrder only maps buy→yes and sell→no).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.bridge.dashboard_security import minimal_subprocess_env  # noqa: E402
from apps.bridge.pmxt_cli import pmxt_argv  # noqa: E402

ENV_FILE = ROOT / "pmxt" / ".env"
API_BASE = os.environ.get("KALSHI_BASE_URL", "https://external-api.kalshi.com").rstrip("/")
API_PREFIX = "/trade-api/v2"
# Match PMXT Kalshi adapter throttle (100ms) — panic bypasses sidecar so we space requests here.
REQUEST_INTERVAL_SEC = 0.1
_RETRYABLE_HTTP = frozenset({429, 503})


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    raw = ENV_FILE.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        trimmed = line.strip()
        idx += 1
        if not trimmed or trimmed.startswith("#") or "=" not in trimmed:
            continue
        key, val = trimmed.split("=", 1)
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and not val.endswith('"'):
            buf = [val[1:]]
            while idx < len(lines):
                part = lines[idx].rstrip("\n")
                idx += 1
                if part.endswith('"'):
                    buf.append(part[:-1])
                    break
                buf.append(part)
            val = "\n".join(buf)
        elif val.startswith("'") and not val.endswith("'"):
            buf = [val[1:]]
            while idx < len(lines):
                part = lines[idx].rstrip("\n")
                idx += 1
                if part.endswith("'"):
                    buf.append(part[:-1])
                    break
                buf.append(part)
            val = "\n".join(buf)
        else:
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            val = val.replace("\\n", "\n")
        os.environ.setdefault(key, val)


def auth_headers(method: str, path: str) -> dict[str, str]:
    api_key = os.environ.get("KALSHI_API_KEY")
    private_key = os.environ.get("KALSHI_PRIVATE_KEY")
    if not api_key or not private_key:
        raise RuntimeError("Missing KALSHI_API_KEY or KALSHI_PRIVATE_KEY in pmxt/.env")

    timestamp = str(int(time.time() * 1000))
    payload = f"{timestamp}{method.upper()}{path}"
    key = serialization.load_pem_private_key(private_key.encode(), password=None)
    signature = key.sign(
        payload.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256(),
    )
    return {
        "KALSHI-ACCESS-KEY": api_key,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def api_request(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    body: dict | None = None,
    allow_retry: bool = False,
) -> Any:
    full_path = API_PREFIX + path
    url = API_BASE + full_path
    if query:
        url += "?" + urlencode({k: v for k, v in query.items() if v is not None})
    data = json.dumps(body).encode() if body is not None else None
    attempts = 2 if allow_retry else 1
    last_exc: RuntimeError | None = None
    for attempt in range(attempts):
        req = Request(url, data=data, method=method.upper(), headers=auth_headers(method, full_path))
        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            last_exc = RuntimeError(f"Kalshi API {method} {path} failed ({exc.code}): {detail}")
            if allow_retry and exc.code in _RETRYABLE_HTTP and attempt + 1 < attempts:
                time.sleep(REQUEST_INTERVAL_SEC * 10)
                continue
            raise last_exc from exc
    if last_exc:
        raise last_exc
    raise RuntimeError(f"Kalshi API {method} {path} failed")


def pmxt_json(args: list[str]) -> Any:
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


def parse_position_size(raw: dict[str, Any]) -> Decimal:
    if raw.get("position_fp") is not None:
        return Decimal(str(raw["position_fp"]))
    if raw.get("position") is not None:
        return Decimal(str(raw["position"]))
    return Decimal(0)


def close_order_for_position(ticker: str, position: Decimal) -> dict[str, Any]:
    count = abs(position)
    if position > 0:
        side = "yes"
        action = "sell"
    elif position < 0:
        side = "no"
        action = "sell"
    else:
        raise ValueError("zero position")

    return {
        "ticker": ticker,
        "client_order_id": f"pmxtrader-panic-{uuid.uuid4()}",
        "side": side,
        "action": action,
        "type": "market",
        "count_fp": str(count),
        "time_in_force": "fill_or_kill",
        "reduce_only": True,
    }


def fetch_positions() -> list[dict[str, Any]]:
    data = api_request("GET", "/portfolio/positions", allow_retry=True)
    rows = data.get("market_positions") or []
    out: list[dict[str, Any]] = []
    for row in rows:
        size = parse_position_size(row)
        if size == 0:
            continue
        out.append({"ticker": row.get("ticker"), "size": size, "raw": row})
    return out


def cancel_open_orders(*, dry_run: bool) -> list[dict[str, Any]]:
    orders = pmxt_json(["kalshi", "orders", "open", "--local"])
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
            pmxt_json(["kalshi", "order", "cancel", "--order-id", str(order_id), "--local"])
            entry["status"] = "canceled"
        except RuntimeError as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
        results.append(entry)
        if not dry_run:
            time.sleep(REQUEST_INTERVAL_SEC)
    return results


def close_positions(*, dry_run: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for pos in fetch_positions():
        ticker = pos["ticker"]
        size = pos["size"]
        entry = {
            "ticker": ticker,
            "size": str(size),
            "status": "dry_run" if dry_run else "pending",
        }
        if dry_run:
            entry["order"] = close_order_for_position(ticker, size)
            results.append(entry)
            continue
        try:
            body = close_order_for_position(ticker, size)
            resp = api_request("POST", "/portfolio/orders", body=body)
            entry["status"] = "submitted"
            entry["orderId"] = (resp.get("order") or {}).get("order_id")
        except (RuntimeError, ValueError, InvalidOperation) as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
        results.append(entry)
        if not dry_run:
            time.sleep(REQUEST_INTERVAL_SEC)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Kalshi emergency cancel / cash-out")
    parser.add_argument("--cancel-orders", action="store_true")
    parser.add_argument("--close-positions", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.cancel_orders and not args.close_positions:
        parser.error("Specify --cancel-orders and/or --close-positions")

    load_env()
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
            print("=== Cancel resting orders ===")
            for row in report["cancelOrders"]:
                print(f"  {row.get('orderId')} {row.get('marketId')} -> {row.get('status')}")
        if report["closePositions"]:
            print("=== Close positions (market, reduce-only) ===")
            for row in report["closePositions"]:
                extra = f" order={row.get('orderId')}" if row.get("orderId") else ""
                err = f" ({row.get('error')})" if row.get("error") else ""
                print(f"  {row.get('ticker')} size={row.get('size')} -> {row.get('status')}{extra}{err}")

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
