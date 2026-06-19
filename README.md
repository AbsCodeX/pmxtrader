# pmxtrader

Prediction market trading platform with PMXT, MCP, and agentic capabilities.

## Overview

`pmxtrader` is a custom-built prediction market trading system centered around [PMXT](https://www.pmxt.dev/). The project focuses on clean market analysis, CLI tooling, and future expansion into web interfaces and autonomous agents, with strong emphasis on MCP integration and security best practices.

## Goals

- Deliver high-quality, structured market analysis in the terminal
- Build a clean, maintainable integration layer around PMXT
- Enable agentic workflows through MCP
- Maintain strong security standards (pre-commit secret scanning, etc.)
- Serve as a public portfolio project demonstrating professional engineering practices

## Project Structure

| Directory     | Purpose                                      |
|---------------|----------------------------------------------|
| `pmxt/`       | PMXT integration layer (source copy)         |
| `apps/`       | Applications (CLI, dashboard, agents)        |
| `packages/`   | Shared components and utilities              |
| `tools/`      | Paper trading, backtesting, and utilities    |
| `scripts/`    | Project scripts (including security tools)   |
| `docs/`       | Architecture decisions and documentation     |

## Quick start (terminal)

```bash
./scripts/setup-dev.sh              # CLI, build, warm sidecar
source scripts/pmxt-env.sh          # or: direnv allow
./pmx help                          # plain-language shortcuts
./pmx balance                       # Kalshi cash
./pmx poly balance                  # Polymarket US cash (needs Poly US keys)
./pmx quote EVENT_ID USA 1
./pmx poly quote MARKET-SLUG long
```

Live Kalshi credentials go in `pmxt/.env` (see `pmxt/core/docs/SETUP_KALSHI.md`).
Polymarket US (separate keys): `POLYMARKET_US_KEY_ID` / `POLYMARKET_US_SECRET_KEY` — see `pmxt/core/docs/SETUP_POLYMARKET_US.md`.
Kill switch: `./scripts/kill-switch.sh on|off|stop` — see `docs/kalshi-integration.md`.
Prediction Hunt API key (optional, pre-trade research): `PREDICTION_HUNT_API_KEY` in `pmxt/.env`.
Agents: see `AGENTS.md`, `docs/multi-agent.md`, `docs/providers.md`, and `.cursor/skills/`.

```bash
./scripts/new-brief.sh my-market
./pmx scout grok
./pmx trader openai briefs/active/DATE-my-market.md   # after approved: true
./scripts/setup-hermes.sh                             # sync LLM keys once
./scripts/check-providers.sh
./scripts/ph-sports-compare.sh slate nba
./scripts/pmxt-eval.sh --event-id EVENT_ID --outcome-label USA --amount 1 --balance
./scripts/pmxt-watch.sh orderbook OUTCOME_ID
./scripts/pmxt-watch-fills.sh --alert-file briefs/alerts/fills.jsonl
```

Kalshi ↔ PMXT script map: [`docs/kalshi-integration.md`](docs/kalshi-integration.md)  
Polymarket US balance + trading: [`docs/polymarket-us-integration.md`](docs/polymarket-us-integration.md)

## Current Focus

Early development. Priority is building a clean terminal-based analysis experience and establishing strong security safeguards.

## Security

This project treats security as a top priority:

- Pre-commit hook with Python secret scanner
- Strict `.gitignore` for environment and key files
- No secrets committed to the repository

## Status

**Phase:** Early Development  
**Focus:** Terminal analysis tooling + security foundation

## License

MIT
