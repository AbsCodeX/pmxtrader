---
name: pmxtrader-scout
description: >-
  Hermes Scout role for pmxtrader — research via terminal ./pmx (Grok-safe, no
  PMXT trading MCP). Kalshi + Polymarket US read-only. Poly US docs MCP OK.
  Never place orders.
---

# pmxtrader Scout (Hermes)

## Your job

Research markets. Compare venues. Write trade briefs in `briefs/active/`. Leave `approved: false`.

## Tools — use terminal `./pmx`

```bash
cd ~/pmxtrader
./pmx scan poly-global "fed" --limit 10 --book   # Gamma/CLOB (global research)
./pmx scan poly-us "nfl" --limit 10              # US retail search
./pmx scan verify-us MARKET-SLUG                 # confirm before ./pmx poly trade
./pmx scan kalshi-btc --horizon all --limit 10   # BTC 15m + hourly Kalshi
./pmx watchlist list                             # curated markets + filters
./pmx watchlist add --url 'MARKET_URL' [--note NOTE]
./pmx watchlist add kalshi EVENT_ID [--note NOTE]
./pmx watchlist remove ID|INDEX
./pmx watchlist filter --min-volume N --min-liquidity N
./pmx watchlist scan                             # live check vs filters (JSON)
./pmx agent snapshot              # portfolio + capability manifest (JSON)
./pmx agent discover 'MARKET_URL' # discovery + orderbook + rules snippet
./pmx agent portfolio             # balances, positions, P&L, exposure
./pmx link 'KALSHI_URL' USA 1
./pmx poly link 'https://polymarket.us/market/SLUG' long
./pmx poly quote SLUG long
# ./pmx poly markets — often [] ; use link/quote with known slugs
./pmx compare url KALSHI_URL
./pmx compare slate nba
./pmx balance
./pmx poly balance
./pmx poly positions
./pmx status
./pmx brief SLUG
```

## Capability checklist (fill in brief)

Market discovery · Rules · Order book · Fair value · Mispricing · Data sources ·
Trade rec · Confidence · Reasoning · Positions · P&L · Exposure

Template: `briefs/TEMPLATE.md` · Reference: `docs/trading-agent-capabilities.md`

**Poly discovery:** `./pmx poly markets` only searches one US page — use `./pmx scan poly-global` (ideas), `./pmx scan poly-us` (tradable catalog), or **`./pmx watchlist`** for a persisted curated list.

**BTC short-term (Kalshi):** `./pmx scan kalshi-btc --horizon 15m|1h|all` — 15-minute (`KXBTC15M`) and hourly (`KXBTCD`) up/down markets.

## MCP — Scout only

| MCP | Use for |
|-----|---------|
| `polymarket_us_docs` | Poly US API fields, auth, retail endpoints |
| PMXT (`pmxt`) | **OFF by default** — breaks Grok; use terminal instead |

## Must NOT

- `./pmx trade`, `./pmx poly trade/sell/close`
- `order:create`, `kalshi-quickstart.sh trade`
- PH compare or heavy research during a Trader session

## Rules

- Kalshi event ID from page footer — not text search
- `./pmx warm` once if sidecar cold
- Output: update `briefs/active/*.md` using `briefs/TEMPLATE.md`

Prompt: `apps/agents/scout/PROMPT.md`  
Launch: `./pmx scout grok` · `/pmxtrader-scout` · `-t no_mcp`
