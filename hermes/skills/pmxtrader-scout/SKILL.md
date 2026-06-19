---
name: pmxtrader-scout
description: >-
  Hermes Scout role for pmxtrader — research via terminal CLI (Grok-safe, no MCP).
  Use ph-sports-compare.sh and pmxt read-only commands. No orders.
---

# pmxtrader Scout (Hermes)

**Do not use PMXT MCP tools with Grok/xAI** — they cause HTTP 400 schema errors.
Use the **terminal** tool to run repo commands. Prefer plain-language shortcuts:

```bash
cd ~/pmxtrader
./pmx link 'KALSHI_URL' USA 1    # paste link → full analysis
./pmx balance
./pmx quote EVENT_ID USA 1
./pmx compare url KALSHI_URL
./pmx brief SLUG
./pmx status
```

Full command list: skill `pmxtrader-commands` or `./pmx help`.

Polymarket US API/docs: use MCP `polymarket_us_docs` or [docs.polymarket.us/mcp](https://docs.polymarket.us/mcp). See `docs/polymarket-us-integration.md`.

## Rules

- Write findings to `briefs/active/*.md`
- Leave `approved: false`
- Never `order:create` or `kalshi-quickstart.sh trade`
- Event ID from Kalshi page footer — not text search

Prompt: `apps/agents/scout/PROMPT.md`

Launch: `./pmx scout grok` or `./scripts/agent-run.sh scout hermes` or `/pmxtrader-scout` with `-t no_mcp`
