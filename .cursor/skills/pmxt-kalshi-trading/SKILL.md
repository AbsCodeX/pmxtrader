---
name: pmxt-kalshi-trading
description: >-
  Fast live Kalshi trading via PMXT CLI. Use when the user wants Kalshi quotes,
  balances, positions, or orders; when evaluating markets from Kalshi URLs; or
  when speed matters during live sports. Prefer event-id lookups over search.
---

# PMXT Kalshi Trading (live)

## Setup (once per machine)

```bash
./scripts/setup-dev.sh          # installs CLI, builds core, warms sidecar
source scripts/pmxt-env.sh      # or: direnv allow (loads .envrc)
```

Credentials live in `pmxt/.env` (`KALSHI_API_KEY`, `KALSHI_PRIVATE_KEY`). Never commit or echo them.

## Execution rules (speed)

0. **Kill switch:** `./scripts/kill-switch.sh status` — if ENGAGED, do not trade
1. **Warm sidecar first:** `./scripts/pmxt-warm.sh` or `pmxt kalshi balance --local --json`
2. **Never search during live games** — use event ID from Kalshi page footer
3. **Max 2 CLI calls** before presenting a trade to the user (event → order)
4. **Do not use MCP or Router** for single-venue in-game execution
5. **Do not chain sleeps or retry loops** — batch reads; avoid 429 rate limits
6. **Real money** — confirm size/side with user before `order:create`

## Fast path (copy-paste for user)

```bash
# Quote (~0.3s with warm sidecar)
pmxt kalshi event --event-id KXWCGAME-26JUN19USAAUS --local --json

# Order (user must confirm)
pmxt kalshi order:create --local \
  --market-id <id> --outcome-id <id> \
  --side buy --type limit --price 0.04 --amount 1 --json
```

Or via wrapper:

```bash
./scripts/kalshi-quickstart.sh event KXWCGAME-26JUN19USAAUS
./scripts/kalshi-quickstart.sh eval KXWCGAME-26JUN19USAAUS USA 1
./scripts/kalshi-quickstart.sh trade MARKET_ID OUTCOME_ID 1
```

Evaluation + streaming (Scout / pre-trade):

```bash
./scripts/pmxt-eval.sh --event-id EVENT --outcome-label USA --amount 1 --balance
./scripts/pmxt-watch.sh orderbook OUTCOME_ID --max-messages 10
./scripts/pmxt-watch-fills.sh --market-ticker OUTCOME_ID --alert-file briefs/alerts/fills.jsonl
./scripts/pmxt-monitor.sh --event-id EVENT --once
```

See `docs/kalshi-integration.md` for full Kalshi API mapping.

Emergency: `./scripts/kill-switch.sh stop` or `stop --cash-out`

## Event ID from Kalshi URL

Kalshi market pages show **Series** and **Event** tickers in the page footer. Copy the Event ticker (e.g. `KXWCGAME-26JUN19USAAUS`). Do not guess search terms.

## Agent role

- **Prepare** commands; user runs or explicitly approves trades
- Use `pmxt` global CLI (`PMXT_CLI_MODE=global`), not vendored `node pmxt/...` unless global missing
- Read-only market data needs no venue keys; trading needs `pmxt/.env`

## MCP (research only)

Start with `./scripts/start-pmxt-mcp.sh` for cross-venue discovery — **not** for live order execution.

## References

- `pmxt/core/docs/SETUP_KALSHI.md`
- `AGENTS.md` — sidecar lock file, `--local` behavior
- `scripts/kalshi-quickstart.sh`
