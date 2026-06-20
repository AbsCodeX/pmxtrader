"""Live data snapshots for the cockpit UI."""

from __future__ import annotations

import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from apps.bridge import parse
from apps.cockpit.bridge import pmx
from apps.cockpit.bridge.history import record

ROOT = Path(__file__).resolve().parents[3]

_HEADER_WORDS = frozenset(
    {"ticker", "market", "symbol", "outcome", "side", "size", "price", "total", "slug", "title"}
)
_health_poll_counter = 0
HEAVY_HEALTH_EVERY = 3
_BALANCE_TIMEOUT = 20
_POSITIONS_TIMEOUT = 30


@dataclass
class LiveSnapshot:
    ok: bool = False
    kill_switch: str = "?"
    read_only: bool = True
    max_trade_contracts: float | None = 10.0
    live_mode: bool = False
    kalshi_available: str | None = None
    kalshi_total: str | None = None
    poly_available: str | None = None
    poly_total: str | None = None
    status_text: str = ""
    sidecar_ok: bool = False
    markets: list[dict] = field(default_factory=list)
    positions_preview: str = ""
    health_lines: list[str] = field(default_factory=list)
    health_checks: list[tuple[str, bool]] = field(default_factory=list)
    health_score: int = 0
    health_total: int = 0
    positions_count: int = 0
    spark_kalshi: list[float] = field(default_factory=list)
    spark_poly: list[float] = field(default_factory=list)


def _count_positions(body: str) -> int:
    body = body.strip()
    if not body or body == "(empty)":
        return 0
    try:
        data = json.loads(body)
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            for key in ("positions", "orders", "data", "markets"):
                rows = data.get(key)
                if isinstance(rows, list):
                    return len(rows)
    except json.JSONDecodeError:
        pass

    count = 0
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("===", "---", "#", "(", "[")):
            continue
        tokens = stripped.split()
        if tokens and all(token.lower() in _HEADER_WORDS for token in tokens):
            continue
        count += 1
    return count


def _apply_balances(snap: LiveSnapshot, kalshi: tuple[str | None, str | None], poly: tuple[str | None, str | None]) -> None:
    k_avail, k_total = kalshi
    p_avail, p_total = poly
    if k_avail is not None:
        snap.kalshi_available = k_avail
    if k_total is not None:
        snap.kalshi_total = k_total
    if p_avail is not None:
        snap.poly_available = p_avail
    if p_total is not None:
        snap.poly_total = p_total


def _fetch_balances_parallel() -> tuple[tuple[str | None, str | None], tuple[str | None, str | None]]:
    with ThreadPoolExecutor(max_workers=2) as pool:
        fk = pool.submit(pmx.run_pmx, "balance", timeout=_BALANCE_TIMEOUT)
        fp = pool.submit(pmx.run_pmx, "poly", "balance", timeout=_BALANCE_TIMEOUT)
        k_out = fk.result().get("stdout") or ""
        p_out = fp.result().get("stdout") or ""
    return parse.parse_balance_json(k_out), parse.parse_balance_json(p_out)


def fetch_snapshot(include_markets: bool = False, market_query: str = "") -> LiveSnapshot:
    snap = LiveSnapshot()
    with ThreadPoolExecutor(max_workers=2) as pool:
        status_f = pool.submit(pmx.run_pmx, "status", timeout=45)
        balances_f = pool.submit(_fetch_balances_parallel)
        r = status_f.result()
        kalshi_bal, poly_bal = balances_f.result()

    snap.ok = r.get("ok", False)
    snap.status_text = r.get("stdout") or r.get("stderr") or r.get("error") or ""
    snap.sidecar_ok = snap.ok and "available:" in snap.status_text

    s = parse.parse_status(snap.status_text)
    snap.kill_switch = s.kill_switch
    from apps.bridge.trade_safety import safety_snapshot

    safety = safety_snapshot(ROOT)
    snap.read_only = safety.read_only
    snap.max_trade_contracts = safety.max_trade_contracts
    snap.live_mode = safety.live_mode
    _apply_balances(snap, kalshi_bal, poly_bal)
    # Fall back to status parse when direct venue fetch unavailable (cold sidecar, missing keys).
    if snap.kalshi_available is None and s.kalshi_available is not None:
        snap.kalshi_available = s.kalshi_available
        snap.kalshi_total = s.kalshi_total
    if snap.poly_available is None and s.poly_available is not None:
        snap.poly_available = s.poly_available
        snap.poly_total = s.poly_total

    hist = record(snap.kalshi_available, snap.poly_available)
    snap.spark_kalshi = hist.get("kalshi", [])
    snap.spark_poly = hist.get("poly", [])

    if include_markets:
        snap.markets = fetch_poly_markets(market_query)
    return snap


def fetch_dashboard() -> LiveSnapshot:
    global _health_poll_counter  # noqa: PLW0603
    snap = fetch_snapshot(include_markets=True)
    preview, count = _positions_preview()
    snap.positions_preview = preview
    snap.positions_count = count
    full_health = (_health_poll_counter % HEAVY_HEALTH_EVERY) == 0
    _health_poll_counter += 1
    checks = _health_checks(snap, full_probe=full_health)
    snap.health_checks = checks
    snap.health_score = sum(1 for _, ok in checks if ok)
    snap.health_total = len(checks)
    snap.health_lines = _format_health_bars(checks)
    return snap


def _positions_preview() -> tuple[str, int]:
    lines: list[str] = []
    count = 0
    jobs = (
        ("Kalshi", ("positions",)),
        ("Poly", ("poly", "positions")),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [(label, pool.submit(pmx.run_pmx, *args, timeout=_POSITIONS_TIMEOUT)) for label, args in jobs]
        results = [(label, fut.result()) for label, fut in futures]

    for label, r in results:
        body = (r.get("stdout") or "").strip()
        if not body:
            lines.append(f"[#8b9cb5]{label}: none[/]")
            continue
        body_lines = [ln for ln in body.splitlines() if ln.strip()]
        count += _count_positions(body)
        preview = "\n".join(body_lines[:6])
        from apps.cockpit.widgets.rich_escape import escape_rich

        lines.append(f"[#00ff9c]{label}[/]\n[#eef2f8]{escape_rich(preview)}[/]")
    text = "\n\n".join(lines) or "[#8b9cb5]No open positions[/]"
    return text, count


def _health_checks(snap: LiveSnapshot, *, full_probe: bool) -> list[tuple[str, bool]]:
    checks: list[tuple[str, bool]] = [("Sidecar", snap.sidecar_ok)]
    if full_probe:
        with ThreadPoolExecutor(max_workers=2) as pool:
            fk = pool.submit(pmx.run_pmx, "balance", timeout=_BALANCE_TIMEOUT)
            fp = pool.submit(pmx.run_pmx, "poly", "balance", timeout=_BALANCE_TIMEOUT)
            checks.append(("Kalshi API", fk.result().get("ok", False)))
            checks.append(("Poly US API", fp.result().get("ok", False)))
    else:
        checks.append(("Kalshi API", bool(snap.kalshi_available)))
        checks.append(("Poly US API", bool(snap.poly_available)))
    checks.append(("Hermes CLI", shutil.which("hermes") is not None))
    skills = Path.home() / ".hermes" / "skills" / "prediction-markets" / "pmxtrader-commands"
    checks.append(("Hermes skills", skills.is_symlink() or skills.is_dir()))
    checks.append(("pmxt/.env", (ROOT / "pmxt" / ".env").is_file()))
    return checks


def _format_health_bars(checks: list[tuple[str, bool]], width: int = 14) -> list[str]:
    from apps.cockpit.widgets.sparkline import bar_gauge

    out: list[str] = []
    for name, ok in checks:
        pct = 100 if ok else 0
        bar = bar_gauge(pct, 100, width)
        mark = "[#00ff9c]●[/]" if ok else "[#ff4466]○[/]"
        out.append(f"{mark} {name:<14} {bar} {pct:>3}%")
    return out


def fetch_poly_markets(query: str = "", limit: int = 16) -> list[dict]:
    args: list[str] = ["poly", "markets"]
    if query.strip():
        args.append(query.strip())
    r = pmx.run_pmx(*args, timeout=60)
    raw = r.get("stdout") or ""
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            rows = data
        elif isinstance(data, dict):
            rows = data.get("markets") or data.get("data") or []
        else:
            rows = []
        return [_normalize_market(m) for m in rows[:limit]]
    except json.JSONDecodeError:
        return _markets_from_text(raw, limit)


def _normalize_market(m: dict) -> dict:
    title = str(m.get("title") or m.get("question") or m.get("slug") or m.get("id") or "?")[:42]
    slug = str(m.get("slug") or m.get("marketId") or m.get("id") or "")
    vol = m.get("volume") or m.get("volume24h") or m.get("liquidity") or ""
    price = ""
    outcomes = m.get("outcomes") or []
    if outcomes and isinstance(outcomes[0], dict):
        price = outcomes[0].get("price") or outcomes[0].get("lastPrice") or ""
    return {
        "title": title,
        "slug": slug[:28],
        "volume": str(vol)[:10],
        "price": str(price)[:8] if price != "" else "—",
    }


def _markets_from_text(text: str, limit: int) -> list[dict]:
    rows: list[dict] = []
    for line in text.splitlines()[: limit + 5]:
        if line.strip():
            rows.append({"title": line.strip()[:42], "slug": "", "volume": "", "price": "—"})
        if len(rows) >= limit:
            break
    return rows


def fetch_positions_text() -> str:
    chunks: list[str] = []
    for title, args in (
        ("=== Kalshi positions ===", ("positions",)),
        ("=== Poly US positions ===", ("poly", "positions")),
        ("=== Poly US orders ===", ("poly", "orders")),
    ):
        r = pmx.run_pmx(*args, timeout=45)
        body = (r.get("stdout") or r.get("stderr") or "").strip()
        chunks.append(f"{title}\n{body or '(empty)'}\n")
    return "\n".join(chunks)
