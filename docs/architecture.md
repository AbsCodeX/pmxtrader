# Architecture

## Overview

`pmxtrader` is a prediction market trading platform built around PMXT as the core integration layer. Terminal-first workflows (`./pmx`), a Textual cockpit, a web command center, and Hermes agents share one subprocess → PMXT sidecar → venue API chain.

Full directory map: **`docs/project-structure.md`**

## High-Level Architecture

```
pmxtrader/
├── pmx, scripts/         # Entry points (CLI router, servers, quickstarts)
├── apps/
│   ├── bridge/           # Shared Python: commands, parse, trade_safety, security
│   ├── cockpit/          # Textual TUI + cockpit/bridge adapter
│   └── agents/           # Scout / Trader / Monitor prompts
├── dashboard/            # Web command center (static + local API)
├── config/               # agents.json, providers.json (no secrets)
├── docs/, tests/, reviews/
├── briefs/               # Trade briefs (active/ gitignored)
├── pmxt/                 # Vendored PMXT monorepo (sidecar, CLI, SDKs)
├── pmxt-mcp/, molt-pmxt/ # Optional git submodules
└── packages/, tools/     # Reserved scaffolds (see READMEs)

Multi-agent workflow: `docs/multi-agent.md` · `config/agents.json` · `briefs/`
```

## Key Principles

- **PMXT as the core**: Market data and execution go through the PMXT sidecar (`pmxt/`).
- **Secrets in `pmxt/.env` only**: Policy JSON in `config/`; never commit keys.
- **UI does not trade**: Web dashboard blocks live orders; cockpit confirms; Terminal executes.
- **Modular design**: `apps/bridge` (shared) vs `apps/cockpit/bridge` (TUI adapter) vs `scripts/` (shell).

## Technology Stack

- **Languages**: Python (bridge, cockpit, tests), Bash (scripts), HTML/CSS/JS (dashboard)
- **Engine**: TypeScript/npm in vendored `pmxt/` only
- **CI**: GitHub Actions (Python lint/test, secret scan, dependency audit)

## Security Architecture

- Secrets are never committed to the repository
- Pre-commit hook scans for common secret patterns
- GitHub Actions runs additional secret scanning on every push
- Trading safety: kill switch, `trade_safety.py`, dashboard command allowlist — see `reviews/2026-06-19/trading-safety-review.md`

## Network and API transparency

Most pmxtrader commands do **not** call venue APIs directly from Python/shell. The usual chain is:

```
./pmx / cockpit / dashboard  →  subprocess  →  pmxt CLI  →  local sidecar (:3847)  →  Kalshi / Polymarket US
```

| Integration | How you see network activity |
|-------------|------------------------------|
| Terminal `./pmx` | stdout/stderr from CLI |
| PMXT sidecar | `x-pmxt-verbose: true` header → request logs in sidecar |
| Web dashboard | Subprocess output only (no raw venue HTTP) |
| Cockpit TUI | Same as dashboard — activity log shows command + output |
| Prediction Hunt | `ph-sports-compare.sh` — curl with bounded retry |
| Hermes / LLM | Opaque inside `hermes` binary; stderr only |
| Panic flatten | `kalshi-emergency-exit.py` — direct Kalshi REST for position closes (documented in `docs/kalshi-integration.md`) |

Subprocess environment: dashboard and cockpit use `minimal_subprocess_env()` (`apps/bridge/dashboard_security.py`) — scripts load credentials from `pmxt/.env` themselves.

## Audit trail

| Review | Doc |
|--------|-----|
| Cockpit / scripts / dashboard | `reviews/2026-06-19/cockpit-scripts-dashboard-review.md` |
| API integration | `reviews/2026-06-19/api-integration-review.md` |
| Dependencies | `docs/dependencies.md` |
| UI / dashboard | `reviews/2026-06-19/ui-dashboard-review.md` |
| Functionality | `reviews/2026-06-19/functionality-review.md` |
| Trading safety | `reviews/2026-06-19/trading-safety-review.md` |
| Project structure | `reviews/2026-06-19/project-structure-review.md` |
