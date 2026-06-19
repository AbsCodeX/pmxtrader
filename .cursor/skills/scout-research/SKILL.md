---
name: scout-research
description: >-
  Scout agent for pmxtrader — Prediction Hunt compare, pmxt read-only quotes,
  trade brief writing. Use in research sessions before execution.
---

# Scout research

Read `apps/agents/scout/PROMPT.md`.

## Workflow

1. `./scripts/new-brief.sh SLUG` or open existing brief in `briefs/active/`
2. `./scripts/ph-sports-compare.sh url URL` or `slate SPORT`
3. `./scripts/pmxt-eval.sh --event-id ID --outcome-label LABEL --amount SIZE --balance`
4. Optional live: `./scripts/pmxt-watch.sh orderbook OUTCOME_ID` or `./scripts/pmxt-monitor.sh --event-id ID --interval 30`
5. Fill brief — thesis, prices, fill estimate, proposed trade
6. Human sets `approved: true`

See `docs/kalshi-integration.md` for Kalshi API ↔ script mapping.

## Hermes / CLI launch

```bash
./pmx scout grok          # default (xAI)
./pmx scout claude        # deep research
./pmx brief SLUG
```

Provider routing: `docs/providers.md`

## Polymarket US (integration research)

Docs MCP: [docs.polymarket.us/mcp](https://docs.polymarket.us/mcp) (Cursor + Hermes — read-only, Grok-safe).  
Trading keys: `POLYMARKET_US_KEY_ID` / `POLYMARKET_US_SECRET_KEY` in `pmxt/.env`.  
Guide: `docs/polymarket-us-integration.md`

## No orders

Never `order:create` or `kalshi-quickstart.sh trade`.
