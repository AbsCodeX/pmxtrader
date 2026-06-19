---
name: pmxt-cli
description: >-
  PMXT CLI and local sidecar usage for pmxtrader. Use when running pmxt
  commands, debugging sidecar/auth, or choosing between --local and --hosted.
---

# PMXT CLI (pmxtrader)

## CLI resolution

```bash
source scripts/pmxt-env.sh
pmxt_cli kalshi balance --local --json   # wrapper function
pmxt kalshi balance --local --json       # same if global installed
```

Prefer **global** `@pmxt/cli` over vendored `node pmxt/sdks/cli/bin/pmxt.js`.

## Local vs hosted

| Mode | Flag | When |
|------|------|------|
| Local sidecar | `--local` | Kalshi/Polymarket trading with keys in `pmxt/.env` |
| PMXT hosted | `--hosted` | Router, cross-venue matching, some feed APIs |

Kalshi live trading: always `--local`.

## Sidecar

- Auto-started by `pmxt ... --local` via `~/.pmxt/server.lock`
- Manual `npm run server` in `pmxt/` may be replaced by ensure-server — read lock file for port/token
- Warm before sessions: `./scripts/pmxt-warm.sh`

## Common commands

```bash
pmxt kalshi balance --local --json
pmxt kalshi event --event-id EVENT_ID --local --json
pmxt kalshi positions --local --json
pmxt kalshi order:create --local --market-id M --outcome-id O --side buy --type limit --price 0.50 --amount 1 --json
pmxt auth login   # hosted API key → ~/.pmxt/cli-auth.json
```

## Project scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup-dev.sh` | Full dev setup |
| `scripts/pmxt-env.sh` | Export paths + `pmxt_cli` helper |
| `scripts/pmxt-warm.sh` | Warm sidecar |
| `scripts/kalshi-quickstart.sh` | Live Kalshi shortcuts |
| `scripts/start-pmxt-mcp.sh` | MCP server (research) |

## Docs

- `pmxt/core/docs/SETUP_KALSHI.md`
- `AGENTS.md`
