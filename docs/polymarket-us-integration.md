---
description: Polymarket US retail API, MCP docs, and ./pmx poly commands.
---

<div class="pmx-page-hero" markdown="1">

# Polymarket US integration

<p class="pmx-page-lead">
Maps Polymarket US documentation to pmxtrader tooling. Docs MCP for research; execution via <code>./pmx poly</code>.
</p>

</div>

## What Polymarket US MCP is

[docs.polymarket.us/mcp](https://docs.polymarket.us/mcp) is a **documentation MCP** (Mintlify HTTP) — not a live trading MCP.

| Tool | Purpose |
|------|---------|
| `search_polymarket_us_documentation` | Semantic search across US docs |
| `query_docs_filesystem_polymarket_us_documentation` | Read/search doc pages (`head`, `rg`, `cat` on virtual FS) |

Use it when building Polymarket US features, debugging auth, or looking up order API fields. **Execution** goes through `./pmx poly` (see below).

## Editor MCP (IDE)

Project config: `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "polymarket-us-docs": {
      "url": "https://docs.polymarket.us/mcp"
    }
  }
}
```

Reload Cursor after changes. No API key required for the docs MCP.

## Hermes

Enabled by default in `./scripts/setup-hermes.sh` (Grok-safe — docs only):

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  polymarket_us_docs:
    url: https://docs.polymarket.us/mcp
    enabled: true
```

Manual toggle:

```bash
python3 scripts/enable-hermes-polymarket-us-mcp.py enable ~/.hermes/config.yaml
python3 scripts/enable-hermes-polymarket-us-mcp.py disable ~/.hermes/config.yaml
```

**Do not confuse with PMXT MCP** (`@pmxt/mcp`) — that is multi-venue trading and breaks on Grok. Polymarket US docs MCP is fine on all providers.

## API keys → PMXT

| Portal | `pmxt/.env` |
|--------|-------------|
| Key ID | `POLYMARKET_US_KEY_ID` |
| Secret Key | `POLYMARKET_US_SECRET_KEY` |

Get keys: [polymarket.us/developer](https://polymarket.us/developer)

Setup guide: `pmxt/core/docs/SETUP_POLYMARKET_US.md`

## PMXT exchange id + `./pmx poly`

```bash
./pmx poly balance
./pmx poly positions
./pmx poly quote MARKET-SLUG long
./pmx poly trade MARKET-SLUG long 1
./pmx poly trade MARKET-SLUG long 10 0.55   # limit buy
./pmx poly sell MARKET-SLUG long 100        # market sell
./pmx poly sell MARKET-SLUG long 50 0.60     # limit sell
./pmx poly close MARKET-SLUG long             # sell full position
./pmx poly watch book MARKET-SLUG long --max-messages 10
./pmx poly watch trades MARKET-SLUG long --max-messages 10
./pmx poly history [MARKET-SLUG] --limit 20
./pmx poly orders
./pmx poly cancel ORDER_ID
./pmx poly cancel-all [MARKET-SLUG]
pmxt polymarket_us markets --limit 5 --local --json
```

Setup: `pmxt/core/docs/SETUP_POLYMARKET_US.md`

## Scout vs Trader (agents)

| Role | Polymarket US docs MCP | Terminal research | Live Poly US orders |
|------|------------------------|-------------------|---------------------|
| **Scout** | ✅ API lookup | ✅ `./pmx poly quote/link/markets` | ❌ never |
| **Trader** | ❌ not during live | ✅ `./pmx poly quote` only (max 2 prep calls) | ✅ `./pmx poly trade/sell/close` (human confirms) |

Hermes bundles: `/pmxtrader-scout`, `/pmxtrader-trader` · Setup: `./scripts/setup-hermes.sh`  
Agent commands: **`docs/commands.md`** · `hermes/README.md`

Cross-venue **research** from Kalshi links still uses Prediction Hunt / PMXT Router (often international Polymarket, not US).

## Emergency flatten (panic)

`./pmx panic` now includes **Polymarket US** when `POLYMARKET_US_*` keys are in `pmxt/.env`:

1. Engages kill switch
2. Cancels all resting Poly US orders (`scripts/polymarket-us-emergency-exit.py`)
3. Market-sells all open positions (when `--cash-out`, the default for `./pmx panic`)

Preview without execution:

```bash
./pmx stop dry
# or
./scripts/kill-switch.sh stop --dry-run --cash-out
```

Implementation mirrors Kalshi panic (`scripts/kalshi-emergency-exit.py`) and supports `--dry-run`.

## Related

- **Command reference:** `docs/commands.md`
- Kalshi workflow: `docs/kalshi-integration.md`
- Hermes MCP policy: `hermes/README.md`
- Multi-agent: `docs/multi-agent.md`
- International Polymarket: `pmxt/core/docs/SETUP_POLYMARKET.md`
