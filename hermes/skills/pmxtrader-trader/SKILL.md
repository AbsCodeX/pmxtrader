---
name: pmxtrader-trader
description: >-
  Hermes Trader role for pmxtrader — approved brief only, max 2 pmxt calls, no
  research tools.
---

# pmxtrader Trader (Hermes)

Same rules as `.cursor/skills/trader-execute/`.

Use Hermes **terminal** to run commands (PMXT MCP is off for Grok):

```bash
cd ~/pmxtrader
./pmx status          # kill switch must be OFF
./pmx link URL USA 1  # if starting from Kalshi link
./pmx quote EVENT USA 1
./pmx trade MARKET OUTCOME 1   # only after human confirms in chat
```

Full command list: skill `pmxtrader-commands` or `./pmx help`.

Never run `./pmx trade` or `./pmx panic` without explicit human confirmation in the session.

Use with: `hermes chat --cli --skills pmxtrader-trader,multi-agent-handoff`

Or: `./pmx trader openai briefs/active/BRIEF.md`
