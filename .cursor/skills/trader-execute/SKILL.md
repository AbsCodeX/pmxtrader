---
name: trader-execute
description: >-
  Trader agent for pmxtrader — execute from approved brief only, max 2 pmxt
  CLI calls, no PH/MCP. Use in execution sessions after Scout handoff.
---

# Trader execute

Read `apps/agents/trader/PROMPT.md`.

## Gate

Brief must have `approved: true`.
Kill switch must be OFF (`./pmx status`).

## Workflow

1. Read attached `briefs/active/*.md` — check `venue` and `approved: true`
2. `./pmx status` — kill switch OFF
3. `./pmx warm` if needed
4. Max 2 prep calls: `./pmx quote` or `./pmx poly quote`
5. Present order command — human confirms and runs:
   - Kalshi: `./pmx trade MARKET OUTCOME SIZE`
   - Poly US: `./pmx poly trade/sell/close SLUG long ...`
6. Optional: `./pmx fills` or `./pmx poly history`

Emergency: `./pmx stop orders` · `./pmx poly cancel-all` · `./pmx panic`

Commands: `docs/commands.md`

## Hermes / CLI launch

```bash
./pmx trader openai briefs/active/BRIEF.md
```

Provider routing: `docs/providers.md`

## Forbidden

PH scripts, MCP, Router, search, re-research

See also: `.cursor/skills/pmxt-kalshi-trading/`
