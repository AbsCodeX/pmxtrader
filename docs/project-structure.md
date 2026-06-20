# Project structure

Last reviewed: **2026-06-19** (Batch J — see `reviews/2026-06-19/project-structure-review.md`).

`pmxtrader` is a thin orchestration layer around the vendored **`pmxt/`** engine. Application code lives under `apps/`, `dashboard/`, and `scripts/`.

---

## Top-level layout

```
pmxtrader/
├── pmx                     # CLI shim → scripts/pmx.sh
├── apps/
│   ├── bridge/             # Shared Python: commands, parse, trade_safety, dashboard_security
│   ├── cockpit/            # Textual TUI (screens, widgets, cockpit/bridge adapter)
│   └── agents/             # Scout / Trader / Monitor prompts (no runtime code)
├── dashboard/              # Web command center (HTML/CSS/JS) — NOT apps/dashboard/
├── scripts/                # Shell entry points, venue quickstarts, agents, servers
├── config/                 # Agent/provider policy JSON (no secrets)
├── docs/                   # pmxtrader-owned documentation
├── tests/                  # Python tests (bridge, cockpit, functionality, safety)
├── reviews/                # Audit mirrors (2026-06-19)
├── briefs/                 # Trade briefs (active/ gitignored)
├── hermes/                 # Hermes skill mirrors
├── pmxt/                   # Vendored PMXT monorepo (sidecar, CLI, SDKs)
├── pmxt-mcp/               # Git submodule (optional MCP server)
├── molt-pmxt/              # Git submodule (optional)
├── packages/               # Reserved (empty scaffold)
└── tools/                  # Reserved (empty scaffold)
```

---

## Main entry points

| Command | Script / module | Purpose |
|---------|-----------------|---------|
| `./pmx …` | `scripts/pmx.sh` | Plain-language CLI router |
| `./pmx cockpit` | `scripts/pmxt-cockpit.sh` → `python -m apps.cockpit` | Textual dashboard |
| `./pmx dashboard` | `scripts/pmxt-dashboard.sh` → `pmxt-dashboard-server.py` | Web UI + safe API |
| `./pmx scout\|trader` | `scripts/agent-run.sh` | Hermes agents |
| Sidecar | `scripts/pmxt-server.sh` | Local PMXT HTTP (:3847) |
| Kill switch | `scripts/kill-switch.sh` | File-based trading halt |

Offline dashboard bookmark: root `index.html` redirects to `dashboard/index.html`.

---

## Layer separation

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **UI** | `dashboard/`, `apps/cockpit/` | Presentation; no venue keys in browser |
| **Shared bridge** | `apps/bridge/` | Command classification, parsing, trade guards, dashboard security |
| **Cockpit adapter** | `apps/cockpit/bridge/` | TUI-specific subprocess wrappers (`pmx.py`, `live.py`, `ai.py`) |
| **Shell / API** | `scripts/` | Subprocess to `pmxt` CLI; Kalshi/Poly quickstarts; dashboard HTTP |
| **Engine** | `pmxt/` | Sidecar, exchange adapters, `@pmxt/cli` (vendor) |
| **Secrets** | `pmxt/.env` only | Venue API keys — never in `config/` or repo |

Wallet/private-key handling stays inside PMXT and venue scripts loading `pmxt/.env`. pmxtrader does not implement on-chain wallet logic.

---

## Config separation

| File | Contents |
|------|----------|
| `config/agents.json` | Scout/Trader allowlists, humanGate, workflow |
| `config/providers.json` | LLM model hints (non-secret) |
| `pmxt/.env` | `KALSHI_*`, `POLYMARKET_US_*`, LLM keys |
| `~/.pmxt/cli-auth.json` | PMXT hosted API key (operator machine) |
| `KILL_SWITCH` | File sentinel at repo root (gitignored) |

---

## Naming notes

| Name | Meaning |
|------|---------|
| `apps/bridge/` | Shared Python library for dashboard + tests |
| `apps/cockpit/bridge/` | Cockpit-only adapter (imports `apps.bridge`) |
| `dashboard/` (root) | Live web assets served by dashboard server |
| `apps/dashboard/` | **Deprecated empty placeholder** — do not use |
| `pmxt/` | Upstream PMXT — bump via submodule/sync intentionally |

---

## Reserved / empty directories

These exist as scaffold placeholders (see each `README.md`):

- `apps/cli/` — terminal entry is `./pmx`, not a separate app
- `apps/dashboard/` — use root `dashboard/` instead
- `packages/shared/`, `packages/ui-components/` — future shared TS (unused)
- `tools/backtesting/`, `tools/paper-trading/` — future utilities

Root `dist/` and root `package.json` TypeScript devDeps are early scaffold (see `AGENTS.md`, `docs/dependencies.md`).
