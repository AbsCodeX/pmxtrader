# Architecture

## Overview

`pmxtrader` is a prediction market trading platform built around PMXT as the core integration layer. The project is designed to support both terminal-based workflows and future expansion into web interfaces and autonomous agents.

## High-Level Architecture

```
pmxtrader/
├── pmxt/                 # PMXT integration layer (source copy)
│   ├── client/           # API wrappers and client logic
│   ├── analysis/         # Market analysis and reporting
│   ├── mcp/              # MCP tools for AI agents
│   └── cli/              # Custom CLI commands
├── apps/                 # Applications
│   ├── dashboard/        # Web interface (future)
│   ├── agents/           # Scout / Trader / Monitor prompts + README
│   └── cli/              # Terminal tools
├── packages/             # Shared code
├── tools/                # Utilities and backtesting
└── scripts/              # Project scripts (e.g. security tools)

Multi-agent workflow: `docs/multi-agent.md` · `config/agents.json` · `briefs/`
```

## Key Principles

- **PMXT as the core**: All market data and execution goes through the PMXT layer.
- **Security first**: Pre-commit secret scanning and strict environment handling.
- **Single source of truth**: All work lives inside `pmxtrader`.
- **Modular design**: Clear separation between integration, applications, and tools.

## Technology Stack

- **Language**: TypeScript (primary), Python (supporting)
- **Package Manager**: npm
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions

## Security Architecture

- Secrets are never committed to the repository
- Pre-commit hook scans for common secret patterns
- GitHub Actions runs additional secret scanning on every push

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

API integration audit: `reviews/2026-06-19/api-integration-review.md` · Linear [ABI-43](https://linear.app/pmxt/issue/ABI-43/api-integration-review-2026-06-19).
