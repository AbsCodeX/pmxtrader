"""Run ./pmx commands from Telegram with safety checks."""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass

from apps.bridge.telegram_trade import PendingTrade, create_pending_trade, pre_execute_checks
from apps.bridge.trade_safety import format_preflight_report, run_preflight, safety_snapshot
from apps.telegram.config import TelegramConfig

_PMX_TRADE_RE = re.compile(
    r"^\./pmx\s+(?:(poly)\s+)?(trade|sell|close)\s+(.+)$",
    re.I,
)


@dataclass(frozen=True)
class PmxResult:
    ok: bool
    stdout: str
    stderr: str
    exit_code: int


def run_pmx(cfg: TelegramConfig, args: list[str], *, timeout: int = 90) -> PmxResult:
    cmd = [str(cfg.root / "pmx"), *args]
    env = os.environ.copy()
    env["PMXTRADER_ROOT"] = str(cfg.root)
    try:
        proc = subprocess.run(
            cmd,
            cwd=cfg.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return PmxResult(
            ok=proc.returncode == 0,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
            exit_code=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        return PmxResult(ok=False, stdout="", stderr=f"Timed out after {timeout}s", exit_code=124)
    except OSError as exc:
        return PmxResult(ok=False, stdout="", stderr=str(exc), exit_code=1)


def status_text(cfg: TelegramConfig) -> str:
    snap = safety_snapshot(cfg.root)
    lines = [
        "Session status",
        f"Kill switch: {snap.kill_switch}",
        f"Read-only: {'ON' if snap.read_only else 'OFF'}",
        f"Live mode file: {'yes' if snap.live_mode else 'no'}",
        f"Max contracts/order: {snap.max_trade_contracts}",
    ]
    if snap.kill_switch_reason:
        lines.append(f"Reason: {snap.kill_switch_reason}")
    warm = run_pmx(cfg, ["warm"], timeout=45)
    if warm.stdout:
        lines.append("")
        lines.append(warm.stdout[:800])
    return "\n".join(lines)


def preflight_text(cfg: TelegramConfig) -> str:
    report = run_preflight(cfg.root)
    return format_preflight_report(report, root=cfg.root)


def go_live(cfg: TelegramConfig) -> PmxResult:
    return run_pmx(cfg, ["go-live"], timeout=30)


def parse_trade_command(line: str) -> tuple[str, list[str]] | None:
    stripped = line.strip()
    if not stripped.startswith("./pmx"):
        return None
    match = _PMX_TRADE_RE.match(stripped)
    if not match:
        return None
    poly, action, rest = match.groups()
    parts = rest.split()
    if poly:
        cmd = ["poly", action.lower(), *parts]
        venue = "polymarket_us"
    else:
        cmd = [action.lower(), *parts]
        venue = "kalshi"
    return venue, cmd


def queue_trade_from_command(
    cfg: TelegramConfig,
    *,
    chat_id: str | int,
    command_line: str,
) -> tuple[PendingTrade | None, str]:
    parsed = parse_trade_command(command_line)
    if not parsed:
        return None, "Not a live trade command (expected ./pmx trade … or ./pmx poly trade …)"
    venue, cmd_args = parsed
    guard = pre_execute_checks(root=cfg.root, chat_id=chat_id)
    if not guard.ok:
        return None, guard.error

    if cmd_args[0] == "poly":
        preview_args = ["preview", "poly", *cmd_args[1:]]
    else:
        preview_args = ["preview", *cmd_args]

    preview = run_pmx(cfg, preview_args, timeout=60)
    preview_text = preview.stdout or preview.stderr or command_line
    pending = create_pending_trade(
        chat_id=chat_id,
        command=cmd_args,
        preview=preview_text,
        venue=venue,
    )
    return pending, preview_text


def execute_pending_trade(cfg: TelegramConfig, pending: PendingTrade) -> PmxResult:
    guard = pre_execute_checks(root=cfg.root, chat_id=pending.chat_id)
    if not guard.ok:
        return PmxResult(ok=False, stdout="", stderr=guard.error, exit_code=1)

    env = os.environ.copy()
    env["PMXTRADER_ROOT"] = str(cfg.root)
    env["PMX_TELEGRAM_CONFIRM"] = "1"
    env["PMX_TELEGRAM_TRADE_TOKEN"] = pending.token
    env["PMX_TELEGRAM_CHAT_ID"] = pending.chat_id

    cmd = [str(cfg.root / "pmx"), *pending.command]
    try:
        proc = subprocess.run(
            cmd,
            cwd=cfg.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return PmxResult(
            ok=proc.returncode == 0,
            stdout=(proc.stdout or "").strip(),
            stderr=(proc.stderr or "").strip(),
            exit_code=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        return PmxResult(ok=False, stdout="", stderr="Trade timed out", exit_code=124)
