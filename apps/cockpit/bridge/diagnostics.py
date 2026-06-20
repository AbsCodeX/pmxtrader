"""Health checks for the diagnostics screen."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from apps.cockpit.bridge import pmx

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def _run(cmd: list[str], timeout: int = 30) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or proc.stderr or "").strip()
        return proc.returncode == 0, out[:400] or ("OK" if proc.returncode == 0 else f"exit {proc.returncode}")
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def run_all() -> list[Check]:
    checks: list[Check] = []

    checks.append(Check("PMXTRADER_ROOT", ROOT.is_dir(), str(ROOT)))

    env_file = ROOT / "pmxt" / ".env"
    checks.append(Check("pmxt/.env", env_file.is_file(), "present" if env_file.is_file() else "missing — copy from .env.example"))

    r = pmx.run_script("pmxt-server.sh", "ensure", timeout=45)
    checks.append(Check("PMXT sidecar", r.get("ok", False), r.get("stderr") or r.get("stdout") or "running"[:200]))

    r = pmx.run_pmx("status", timeout=30)
    first = (r.get("stdout") or "").splitlines()[0] if r.get("stdout") else "?"
    checks.append(Check("Kill switch + status", r.get("ok", False), first[:120]))

    r = pmx.run_pmx("balance", timeout=30)
    checks.append(Check("Kalshi balance", r.get("ok", False), _first_line(r)))

    r = pmx.run_pmx("poly", "balance", timeout=30)
    checks.append(Check("Poly US balance", r.get("ok", False), _first_line(r)))

    ok, detail = _run(["bash", str(ROOT / "scripts" / "check-providers.sh")], timeout=20)
    checks.append(Check("LLM providers", ok, detail.splitlines()[0] if detail else "checked"))

    checks.append(Check("Hermes CLI", shutil.which("hermes") is not None, shutil.which("hermes") or "not on PATH"))

    ok, _ = _run(["python3", "-c", "import textual"], timeout=5)
    checks.append(Check("Textual (cockpit UI)", ok, "installed" if ok else "pip install -r requirements-cockpit.txt"))

    skills = Path.home() / ".hermes" / "skills" / "prediction-markets" / "pmxtrader-commands"
    checks.append(Check("Hermes pmxtrader skills", skills.is_symlink() or skills.is_dir(), str(skills)))

    dash = ROOT / "dashboard" / "index.html"
    dash_css = ROOT / "dashboard" / "css" / "app.css"
    dash_ok = dash.is_file() and dash_css.is_file()
    checks.append(Check("Web dashboard assets", dash_ok, "./pmx dashboard"))

    return checks


def _first_line(result: dict) -> str:
    text = (result.get("stdout") or result.get("stderr") or result.get("error") or "")[:200]
    return text.splitlines()[0] if text else "no output"
