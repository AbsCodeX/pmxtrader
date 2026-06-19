#!/usr/bin/env python3
"""Enable or disable Polymarket US documentation MCP in Hermes config.yaml."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

POLYMARKET_US_DOCS_MCP_URL = "https://docs.polymarket.us/mcp"


def configure(path: Path, enabled: bool) -> None:
    cfg = yaml.safe_load(path.read_text()) or {}
    mcp = cfg.setdefault("mcp_servers", {})
    entry = mcp.setdefault("polymarket_us_docs", {})
    entry["url"] = POLYMARKET_US_DOCS_MCP_URL
    entry["enabled"] = enabled
    entry["timeout"] = 120
    entry["connect_timeout"] = 60
    path.write_text(yaml.dump(cfg, default_flow_style=False, sort_keys=False))
    state = "enabled" if enabled else "disabled"
    print(f"Polymarket US docs MCP {state} in {path}")


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: enable-hermes-polymarket-us-mcp.py enable|disable CONFIG_YAML",
            file=sys.stderr,
        )
        return 1

    action = sys.argv[1].lower()
    path = Path(sys.argv[2]).expanduser()

    if action == "enable":
        configure(path, True)
    elif action == "disable":
        configure(path, False)
    else:
        print("Action must be enable or disable", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
