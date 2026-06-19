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

1. Read attached `briefs/active/*.md`
2. `./scripts/pmxt-warm.sh` if needed
3. Max 2 calls: `event --event-id`, `balance`
4. Present `./pmx trade ...` — human confirms and runs
5. Optional: `./scripts/pmxt-watch-fills.sh --market-ticker OUTCOME_ID --alert-file briefs/alerts/fills.jsonl`

Emergency stop: `./pmx stop orders` or `./pmx panic`

## Hermes / CLI launch

```bash
./pmx trader openai briefs/active/BRIEF.md
```

Provider routing: `docs/providers.md`

## Forbidden

PH scripts, MCP, Router, search, re-research

See also: `.cursor/skills/pmxt-kalshi-trading/`
