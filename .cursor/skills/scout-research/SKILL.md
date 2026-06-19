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
2. `./pmx link URL OUTCOME` or `./pmx poly link URL long` or `./pmx compare url URL`
3. `./pmx quote EVENT OUTCOME` or `./pmx poly quote SLUG long`
4. Optional live: `./pmx watch OUTCOME` or `./pmx poly watch book SLUG long`
5. Fill brief — venue, thesis, prices, proposed `./pmx` command
6. Human sets `approved: true`

See `docs/commands.md` · `docs/kalshi-integration.md`

## Hermes / CLI launch

```bash
./pmx scout grok          # default (xAI)
./pmx scout claude        # deep research
./pmx brief SLUG
```

Provider routing: `docs/providers.md`

## Polymarket US (Scout research)

```bash
./pmx poly quote SLUG long
./pmx poly link URL long
./pmx poly markets [query]
```

Docs MCP: [docs.polymarket.us/mcp](https://docs.polymarket.us/mcp) (Cursor + Hermes — read-only).  
Guide: `docs/polymarket-us-integration.md` · Commands: `docs/commands.md`

## No orders

Never `order:create` or `kalshi-quickstart.sh trade`.
