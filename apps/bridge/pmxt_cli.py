"""Resolve PMXT CLI invocation (global pmxt vs vendored node script)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def pmxt_argv(args: list[str], root: Path | None = None) -> list[str]:
    """Build argv for PMXT CLI — mirrors scripts/pmxt-env.sh pmxt_cli."""
    base = root or ROOT
    mode = os.environ.get("PMXT_CLI_MODE", "")
    default_script = str(base / "pmxt" / "sdks" / "cli" / "bin" / "pmxt.js")

    if mode == "vendored":
        script = os.environ.get("PMXT_CLI_SCRIPT", default_script)
        return ["node", script, *args]

    cli_bin = os.environ.get("PMXT_CLI_BIN")
    if cli_bin == "node":
        script = os.environ.get("PMXT_CLI_SCRIPT", default_script)
        return ["node", script, *args]
    if cli_bin:
        return [cli_bin, *args]
    if shutil.which("pmxt"):
        return ["pmxt", *args]
    return ["node", default_script, *args]
