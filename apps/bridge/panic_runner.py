"""Run per-venue panic scripts with optional dry-run resilience."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from apps.bridge.trade_safety import has_kalshi_keys, has_poly_us_keys


@dataclass
class PanicVenueResult:
    venue: str
    script: str
    ok: bool
    output: str = ""
    error: str = ""


@dataclass
class PanicRunReport:
    results: list[PanicVenueResult] = field(default_factory=list)

    @property
    def ran(self) -> bool:
        return bool(self.results)

    @property
    def ok_count(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.ok)


def _first_line(text: str) -> str:
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:240]
    return "unknown error"


def _run_script(script: Path, args: list[str], *, timeout: float = 120.0) -> PanicVenueResult:
    venue = script.stem.replace("-emergency-exit", "").replace("-", " ").title()
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(script.parents[1]),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return PanicVenueResult(venue=venue, script=str(script), ok=False, error=str(exc))
    combined = "\n".join(part for part in (proc.stdout, proc.stderr) if part).strip()
    if proc.returncode == 0:
        return PanicVenueResult(venue=venue, script=str(script), ok=True, output=combined)
    return PanicVenueResult(
        venue=venue,
        script=str(script),
        ok=False,
        output=proc.stdout.strip(),
        error=_first_line(combined) or f"exit {proc.returncode}",
    )


def run_panic_venues(
    root: Path,
    *,
    cancel_orders: bool = True,
    close_positions: bool = False,
    dry_run: bool = False,
    resilient: bool = False,
) -> tuple[int, str]:
    """Run configured venue panic scripts. Returns (exit_code, human output)."""
    args: list[str] = []
    if cancel_orders:
        args.append("--cancel-orders")
    if close_positions:
        args.append("--close-positions")
    if dry_run:
        args.append("--dry-run")

    scripts: list[tuple[str, Path]] = []
    if has_kalshi_keys(root):
        scripts.append(("Kalshi", root / "scripts" / "kalshi-emergency-exit.py"))
    if has_poly_us_keys(root):
        scripts.append(("Polymarket US", root / "scripts" / "polymarket-us-emergency-exit.py"))

    report = PanicRunReport()
    lines: list[str] = []

    if not scripts:
        return 1, "No venue keys configured (Kalshi or Polymarket US)."

    for label, script in scripts:
        if not script.is_file():
            result = PanicVenueResult(
                venue=label,
                script=str(script),
                ok=False,
                error=f"missing script: {script}",
            )
        else:
            result = _run_script(script, args)
            result.venue = label
        report.results.append(result)

        if result.output:
            lines.append(result.output)
        if result.ok:
            continue
        if resilient:
            lines.append(f"WARNING: {label} panic preview failed (continuing): {result.error}")
        elif result.error:
            lines.append(f"ERROR: {label}: {result.error}")

    if resilient:
        lines.append("")
        lines.append(
            f"Panic preview summary: {report.ok_count}/{len(report.results)} venue(s) OK"
            + (f", {report.fail_count} failed (non-fatal in dry-run)" if report.fail_count else "")
        )
        return 0 if report.ran else 1, "\n".join(lines)

    if report.fail_count:
        return 1, "\n".join(lines)
    return 0, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run per-venue panic scripts")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--cancel-orders", action="store_true")
    parser.add_argument("--close-positions", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resilient", action="store_true", help="Continue after venue failures")
    args = parser.parse_args(argv)

    code, output = run_panic_venues(
        args.root,
        cancel_orders=args.cancel_orders,
        close_positions=args.close_positions,
        dry_run=args.dry_run,
        resilient=args.resilient or args.dry_run,
    )
    if output:
        print(output)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
