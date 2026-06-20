"""Shared command classification and allowlists for cockpit + web dashboard."""

from __future__ import annotations

import re

# Read-only / safe dashboard shortcuts
SAFE_COMMANDS: dict[str, list[str]] = {
    "help": ["./pmx", "help"],
    "status": ["./pmx", "status"],
    "warm": ["./pmx", "warm"],
    "preflight": ["./pmx", "preflight"],
    "balance": ["./pmx", "balance"],
    "positions": ["./pmx", "positions"],
    "poly-balance": ["./pmx", "poly", "balance"],
    "poly-positions": ["./pmx", "poly", "positions"],
    "poly-orders": ["./pmx", "poly", "orders"],
    "panic-dry-run": ["./pmx", "panic", "--dry-run"],
    "providers": ["./scripts/check-providers.sh"],
}

BLOCKED_PREFIXES = ("trade", "sell", "close", "panic", "stop", "cancel", "resume")

BLOCKED_TRADE = re.compile(
    r"^\s*(?:\./)?pmx\s+(?:"
    r"trade|panic|"
    r"stop(?:\s|$)|"
    r"poly\s+(?:trade|sell|close|cancel(?:-all)?)"
    r")",
    re.I,
)

MUTATING_CONTROL = re.compile(
    r"^\s*(?:\./)?pmx\s+(?:stop|resume)\b",
    re.I,
)

SAFE_READ = re.compile(
    r"^\s*(?:\./)?pmx\s+(?:"
    r"status|balance|positions|link|quote|event|warm|help|"
    r"poly\s+(?:balance|positions|quote|link|markets|orders|history|watch)"
    r")(?:\s|$)",
    re.I,
)

# Explicit allowlist for command palette (deny-by-default)
PALETTE_COMMANDS: frozenset[str] = frozenset({
    "status",
    "balance",
    "positions",
    "warm",
    "help",
    "preflight",
    "poly balance",
    "poly positions",
    "poly orders",
    "poly markets",
})

# Script shortcuts shown in palette; cockpit confirms before running
PALETTE_SCRIPT_COMMANDS: frozenset[str] = frozenset({"dashboard"})


def normalize_pmx_line(line: str) -> str:
    line = line.strip()
    if line.startswith("./pmx "):
        return line[6:].strip()
    if line.startswith("pmx "):
        return line[4:].strip()
    return line


def classify_command(line: str) -> str:
    line = line.strip()
    if not line:
        return "empty"
    if BLOCKED_TRADE.match(line):
        return "trade"
    if MUTATING_CONTROL.match(line):
        return "mutating"
    if SAFE_READ.match(line) or line.startswith("./scripts/"):
        return "safe"
    if line.startswith("./pmx") or line.startswith("pmx "):
        return "unknown"
    return "other"


def is_palette_allowed(cmd: str) -> bool:
    """Return True if cmd is safe to run from the cockpit command palette."""
    normalized = normalize_pmx_line(cmd if cmd.startswith(("./pmx", "pmx")) else f"./pmx {cmd}")
    if not normalized:
        return False
    if normalized in PALETTE_COMMANDS:
        return True
    if normalized in PALETTE_SCRIPT_COMMANDS:
        return True
    if normalized.startswith("poly markets"):
        return True
    return classify_command(f"./pmx {normalized}") == "safe"


def resolve_dashboard_command(raw: str) -> list[str] | None:
    text = normalize_pmx_line(raw)
    if not text:
        return None
    if text.startswith("./"):
        return None

    parts = text.split()
    if not parts:
        return None

    key = parts[0].lower()
    for blocked in BLOCKED_PREFIXES:
        if key == blocked:
            return None
        if key == "poly" and len(parts) > 1 and parts[1].lower() in (
            "trade", "sell", "close", "cancel", "cancel-all"
        ):
            return None

    if text.lower() in ("panic --dry-run", "panic-dry-run"):
        return SAFE_COMMANDS["panic-dry-run"]

    alias = "-".join(p.lower() for p in parts[:2]) if len(parts) >= 2 and parts[0].lower() == "poly" else key
    if alias in SAFE_COMMANDS:
        return SAFE_COMMANDS[alias]
    if key in SAFE_COMMANDS:
        return SAFE_COMMANDS[key]

    if key == "quote" and len(parts) >= 3:
        return ["./pmx", "quote", parts[1], parts[2], *parts[3:]]
    if len(parts) >= 3 and parts[0].lower() == "poly" and parts[1].lower() == "quote":
        return ["./pmx", "poly", "quote", parts[2], *parts[3:]]
    if key == "link" and len(parts) >= 2:
        return ["./pmx", "link", parts[1], *parts[2:]]
    if len(parts) >= 2 and parts[0].lower() == "poly" and parts[1].lower() == "link":
        return ["./pmx", "poly", "link", parts[2], *parts[3:]]
    if len(parts) >= 2 and parts[0].lower() == "poly" and parts[1].lower() == "markets":
        return ["./pmx", "poly", "markets", *parts[2:]]
    if key == "event" and len(parts) >= 2:
        return ["./pmx", "event", parts[1]]

    return None


def extract_pmx_commands(text: str) -> list[str]:
    found: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("./pmx") or s.startswith("pmx "):
            cmd = s if s.startswith("./") else f"./{s}"
            if cmd not in found:
                found.append(cmd)
    return found
