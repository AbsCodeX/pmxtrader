---
name: multi-agent-handoff
description: >-
  pmxtrader Scout/Trader handoff for Hermes. Separate research and execution
  sessions; briefs in briefs/active/ with approved: true gate.
---

# Multi-agent handoff (Hermes)

Install: `./scripts/install-hermes-skills.sh`

Scout skills: `pmxtrader-scout,multi-agent-handoff` (terminal CLI — no MCP)
Trader skills: `pmxtrader-trader,multi-agent-handoff`

```bash
./pmx scout grok
./pmx trader openai briefs/active/BRIEF.md
```

Config: `config/agents.json` · `docs/providers.md`
