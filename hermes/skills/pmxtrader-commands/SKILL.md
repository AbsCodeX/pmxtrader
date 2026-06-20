---
name: pmxtrader-commands
description: >-
  Complete pmxtrader command reference for Hermes terminal use. Use when the user
  asks what to run, pastes a Kalshi or Polymarket US link, or needs Scout/Trader
  navigation. Always cd to project root and use ./pmx shortcuts. Canonical doc:
  docs/commands.md
---

# pmxtrader command reference (Hermes)

**Always:** `cd ~/pmxtrader` (or `$PMXTRADER_ROOT`). Use Hermes **terminal** tool — PMXT trading MCP is disabled (Grok-safe).

**Sidecar:** `./pmx warm` or `./scripts/pmxt-server.sh restart` after env changes.

**Real money:** Check `./pmx status` (kill switch OFF). Never run trade/sell/close without explicit human confirmation.

## Start a session

```bash
pmxt-terminal              # new macOS Terminal window (from anywhere, after setup-direnv)
pmxt-start                 # current shell (inside repo / direnv)
./pmx session              # same as pmxt-start
./pmx terminal             # same as pmxt-terminal
```

| `./pmx dashboard` | Browser command center + safe mini-terminal |

Setup once: `./scripts/setup-direnv.sh` · Offline shortcuts: open `index.html` in browser

Bootstraps sidecar, warms venues, prints status + cheat sheet.

## Tool routing (pick the right one)

| User wants | Run |
|------------|-----|
| Kalshi link analysis | `./pmx link URL OUTCOME 1` |
| Kalshi quote | `./pmx quote EVENT OUTCOME 1` |
| Poly US link/quote | `./pmx poly link URL long` or `./pmx poly quote SLUG long` |
| Cross-venue odds | `./pmx compare url URL` (Scout only) |
| Poly US API docs | MCP `polymarket_us_docs` (Scout only) |
| Kalshi buy | `./pmx trade MARKET OUTCOME size` |
| Poly US buy/sell/exit | `./pmx poly trade/sell/close SLUG long ...` |
| Live Poly book | `./pmx poly watch book SLUG long --max-messages 10` |
| Balances both venues | `./pmx status` |

## Kalshi

```bash
./pmx link 'https://kalshi.com/markets/kxwcgame/world-cup-game' USA 1
./pmx quote KXEVENT-... USA 1
./pmx balance
./pmx positions
./pmx trade MARKET OUTCOME 1
./pmx watch OUTCOME_ID
./pmx compare url KALSHI_URL
```

## Polymarket US (`./pmx poly`)

```bash
./pmx poly balance
./pmx poly positions
./pmx poly quote SLUG long
./pmx poly link 'https://polymarket.us/market/SLUG' long
./pmx poly trade SLUG long 1
./pmx poly trade SLUG long 10 0.55
./pmx poly sell SLUG long 100
./pmx poly close SLUG long
./pmx poly watch book SLUG long --max-messages 10
./pmx poly watch trades SLUG long --max-messages 10
./pmx poly history --limit 20
./pmx poly orders
./pmx poly cancel ORDER_ID
./pmx poly cancel-all
```

Keys: `POLYMARKET_US_KEY_ID` / `POLYMARKET_US_SECRET_KEY` · `long`=YES, `short`=NO

## Safety

```bash
./pmx status
./pmx warm
./pmx stop on "reason"
./pmx resume
./pmx panic
```

## Agents

```bash
./pmx brief SLUG
./pmx scout grok
./pmx trader openai briefs/active/BRIEF.md
```

Bundles: `/pmxtrader` · `/pmxtrader-scout` · `/pmxtrader-trader` · `-t no_mcp`

## Docs

- `docs/commands.md` — master reference
- `docs/multi-agent.md` — Scout vs Trader
- `docs/polymarket-us-integration.md` — Poly US
- `docs/kalshi-integration.md` — Kalshi
