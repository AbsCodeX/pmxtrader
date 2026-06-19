---
name: pmxtrader-commands
description: >-
  Complete pmxtrader command reference for Hermes terminal use. Use when the user
  pastes a Kalshi link, asks what to run, or needs navigation across Scout/Trader
  workflows. Always run from ~/pmxtrader with ./pmx shortcuts.
---

# pmxtrader command reference (Hermes)

**Always:** `cd ~/pmxtrader` before any command. Use **terminal** only — PMXT MCP is disabled (Grok-safe).

**Real money:** Kalshi live keys. Check `./pmx status` before trades. Never `./pmx trade` without explicit human confirmation.

## Fast path: paste a Kalshi link

```bash
cd ~/pmxtrader
./pmx link 'https://kalshi.com/markets/kxwcgame/world-cup-game' USA 1
# or direct event URL:
./pmx link 'https://kalshi.com/events/KXWCGAME-26JUN19USAAUS' USA 1
```

Series pages with many games need an **outcome label** (team name). Output shows price, book, fill est, balance, and suggested `./pmx trade` line.

## Polymarket US (`./pmx poly`)

| Command | Purpose |
|---------|---------|
| `./pmx poly balance` | US account cash |
| `./pmx poly positions` | Open holdings |
| `./pmx poly quote SLUG long` | Market + orderbook |
| `./pmx poly link URL long` | Quote from polymarket.us link |
| `./pmx poly trade SLUG long 1` | Market buy (kill switch must be OFF) |
| `./pmx poly trade SLUG long 10 0.55` | Limit buy @ price |
| `./pmx poly orders` | Open orders |
| `./pmx poly cancel ORDER_ID` | Cancel order |

Keys: `POLYMARKET_US_KEY_ID` / `POLYMARKET_US_SECRET_KEY` in `pmxt/.env`.  
Guide: `docs/polymarket-us-integration.md`

## Account & safety (Kalshi default)

| Command | Purpose |
|---------|---------|
| `./pmx balance` | Available cash |
| `./pmx positions` | Open holdings |
| `./pmx status` | Kill switch + Kalshi + Poly US balance (if keys set) |
| `./pmx warm` | Start/warm PMXT sidecar |
| `./pmx stop on "reason"` | Block new trades |
| `./pmx resume` | Allow trading again |
| `./pmx stop orders` | Halt + cancel resting orders |
| `./pmx panic` | Halt + cancel + close all (needs human typing PANIC) |

## Research (Scout)

| Command | Purpose |
|---------|---------|
| `./pmx link URL [OUTCOME] [size]` | **URL → full eval snapshot** |
| `./pmx quote EVENT [OUTCOME] [size]` | Eval when you have event ticker |
| `./pmx event EVENT` | Raw event JSON |
| `./pmx compare url URL` | Cross-venue odds (Prediction Hunt) |
| `./pmx compare slate nba` | Sports slate compare |
| `./pmx brief SLUG` | Create trade brief |
| `./pmx scout grok` | Fast Scout agent (default) |
| `./pmx scout claude` | Deep Scout agent |
| `./pmx monitor EVENT --label USA` | Poll prices → alerts |

## Live streaming

| Command | Purpose |
|---------|---------|
| `./pmx watch OUTCOME_ID` | Stream orderbook |
| `./pmx trades OUTCOME_ID` | Public trade tape |
| `./pmx fills [OUTCOME_ID]` | Your fill stream |

## Trade (Trader — human gate)

| Command | Purpose |
|---------|---------|
| `./pmx trader openai briefs/active/BRIEF.md` | Trader from approved brief |
| `./pmx trade MARKET OUTCOME [size]` | **Kalshi** market buy — only after human confirms |
| `./pmx poly trade SLUG long 1` | **Polymarket US** market buy — kill switch OFF + human confirms |
| `./pmx poly trade SLUG long 10 0.55` | Poly US limit buy |

Trader rules: brief must have `approved: true`. Max 2 prep CLI calls. No PH/MCP during live.

## Multi-agent workflow

```bash
./pmx brief my-game
./pmx scout grok          # or: paste link + ask Scout to run ./pmx link
# Scout fills briefs/active/*.md — human sets approved: true
./pmx trader openai briefs/active/DATE-my-game.md
# Human confirms, then: ./pmx trade ...
```

## Event ID fallback

If `./pmx link` fails on a series page, read the **event ticker from the Kalshi page footer** and run:

```bash
./pmx quote KXEVENT-... USA 1
```

## Docs in repo

- `docs/providers.md` — LLM routing (grok/claude/openai)
- `docs/multi-agent.md` — Scout/Trader roles
- `docs/kalshi-integration.md` — API ↔ script map
- `docs/polymarket-us-integration.md` — Poly US keys + [docs MCP](https://docs.polymarket.us/mcp)
- `./pmx help` — full shortcut list

## Hermes bundles

- `/pmxtrader-scout` — research lane
- `/pmxtrader-trader` — execution lane (approved brief only)

Launch: `./pmx scout grok` or `hermes chat --cli -t no_mcp` then `/pmxtrader-scout`
