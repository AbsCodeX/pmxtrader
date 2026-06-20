"""Trading safety guards for pmxtrader-owned live order paths."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
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


_DEFAULT_SIDECAR_PORT = 3847
_KALSHI_ENV_VARS = ("KALSHI_API_KEY", "KALSHI_PRIVATE_KEY")
_POLY_US_ENV_VARS = ("POLYMARKET_US_KEY_ID", "POLYMARKET_US_SECRET_KEY")


def preflight_enabled() -> bool:
    return os.environ.get("PMX_PREFLIGHT", "1").strip().lower() not in ("0", "false", "no")


def sidecar_lock_path() -> Path:
    return Path.home() / ".pmxt" / "server.lock"


def read_sidecar_port(default: int = _DEFAULT_SIDECAR_PORT) -> int:
    lock = sidecar_lock_path()
    if not lock.is_file():
        return default
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
        port = int(data.get("port", default))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default
    return port if port > 0 else default


def _env_file(root: Path) -> Path:
    return root / "pmxt" / ".env"


def _env_has_vars(env_path: Path, names: tuple[str, ...]) -> bool:
    if not env_path.is_file():
        return False
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    values: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        values[key.strip()] = val.strip().strip('"').strip("'")
    return all(values.get(name, "").strip() for name in names)


def has_kalshi_keys(root: Path) -> bool:
    return _env_has_vars(_env_file(root), _KALSHI_ENV_VARS)


def has_poly_us_keys(root: Path) -> bool:
    return _env_has_vars(_env_file(root), _POLY_US_ENV_VARS)


def panic_venues(root: Path) -> list[str]:
    venues: list[str] = []
    if has_kalshi_keys(root):
        venues.append("Kalshi")
    if has_poly_us_keys(root):
        venues.append("Polymarket US")
    return venues


def format_panic_scope(root: Path) -> str:
    venues = panic_venues(root)
    if not venues:
        return "Panic scope: none (no venue keys in pmxt/.env)"
    lines = ["Panic scope (cancel resting orders + market flatten when keys set):"]
    for venue in venues:
        lines.append(f"  {venue}: included")
    return "\n".join(lines)


def check_sidecar_health(*, port: int | None = None, timeout: float = 2.0) -> TradeGuardResult:
    resolved = port if port is not None else read_sidecar_port()
    url = f"http://127.0.0.1:{resolved}/health"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if 200 <= resp.status < 300:
                return TradeGuardResult(True, f"Sidecar OK at {url}")
            return TradeGuardResult(False, f"Sidecar health returned HTTP {resp.status} at {url}")
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        return TradeGuardResult(False, f"Sidecar not reachable at {url} ({reason})")
    except TimeoutError:
        return TradeGuardResult(False, f"Sidecar health timed out at {url}")


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    ok: bool
    detail: str
    fix: str = ""
    blocking: bool = True


@dataclass
class PreflightReport:
    checks: list[PreflightCheck] = field(default_factory=list)
    go: bool = False
    panic_venues: list[str] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "GO" if self.go else "NO-GO"


def run_preflight(root: Path) -> PreflightReport:
    snap = safety_snapshot(root)
    sidecar = check_sidecar_health()
    ks_ok = snap.kill_switch == "OFF"
    ro_ok = not snap.read_only
    kalshi = has_kalshi_keys(root)
    poly = has_poly_us_keys(root)
    keys_ok = kalshi or poly
    cap = snap.max_trade_contracts

    checks = [
        PreflightCheck(
            "Sidecar health",
            sidecar.ok,
            sidecar.error,
            fix="Run: ./pmx warm   (or ./pmx session)",
        ),
        PreflightCheck(
            "Kill switch",
            ks_ok,
            f"{'OFF' if ks_ok else 'ON'}"
            + (f" — {snap.kill_switch_reason}" if snap.kill_switch_reason else ""),
            fix="Run: ./pmx resume   (or ./scripts/kill-switch.sh off)",
        ),
        PreflightCheck(
            "Read-only mode",
            ro_ok,
            "OFF" if ro_ok else "ON (PMX_READ_ONLY or no .pmx-live)",
            fix="Run: ./pmx go-live",
        ),
        PreflightCheck(
            "Max trade size",
            cap is not None and cap > 0,
            f"{cap:g} contracts/order (PMX_MAX_TRADE_CONTRACTS)" if cap else "invalid or unset",
            fix="export PMX_MAX_TRADE_CONTRACTS=10",
            blocking=False,
        ),
        PreflightCheck(
            "Kalshi keys",
            kalshi,
            "present in pmxt/.env" if kalshi else "missing",
            fix="Add KALSHI_API_KEY + KALSHI_PRIVATE_KEY to pmxt/.env",
            blocking=False,
        ),
        PreflightCheck(
            "Polymarket US keys",
            poly,
            "present in pmxt/.env" if poly else "missing",
            fix="Add POLYMARKET_US_KEY_ID + POLYMARKET_US_SECRET_KEY to pmxt/.env",
            blocking=False,
        ),
        PreflightCheck(
            "Venue credentials",
            keys_ok,
            "at least one venue configured" if keys_ok else "no venue keys found",
            fix="Configure Kalshi or Polymarket US keys in pmxt/.env",
        ),
    ]

    blocking_ok = all(c.ok for c in checks if c.blocking)
    report = PreflightReport(checks=checks, go=blocking_ok, panic_venues=panic_venues(root))
    return report


def format_preflight_report(report: PreflightReport, *, root: Path) -> str:
    lines = ["=== pmxtrader preflight ===", ""]
    for check in report.checks:
        mark = "OK" if check.ok else "FAIL"
        lines.append(f"[{mark}] {check.name}: {check.detail}")
        if not check.ok and check.fix:
            lines.append(f"      → {check.fix}")
    lines.append("")
    lines.extend(format_panic_scope(root).splitlines())
    lines.append("")
    lines.append(f"Live trading: {report.verdict}")
    if report.go:
        lines.append("You may place live orders when ready (still confirm each order).")
    else:
        lines.append("Fix blocking items above before ./pmx go-live and live trades.")
    return "\n".join(lines)
