---
name: multi-agent-handoff
description: >-
  pmxtrader multi-agent Scout/Trader handoff. Use when switching research vs
  execution, writing trade briefs, or choosing Cursor/Claude/Codex/Hermes/Grok
  for a role.
---

# Multi-agent handoff

## Roles

| Role | When | Provider options |
|------|------|------------------|
| Scout | Before trade | Grok (default), Claude, OpenAI, Cursor, Codex, Hermes |
| Trader | After brief approved | OpenAI (default), Cursor, Codex, Hermes |
| Human | Approve + run orders | Terminal |

## Commands

```bash
./scripts/new-brief.sh my-market
./pmx scout grok
./pmx scout claude                    # deep research
./pmx trader openai briefs/active/2026-06-19-my-market.md
```

Keys: `pmxt/.env` → `./scripts/setup-hermes.sh` → `./scripts/check-providers.sh`

## Brief approval

Trader refuses unless YAML frontmatter has `approved: true`.

## Separate sessions

Never run Scout research and Trader execution in the same chat with all MCP tools enabled.

## Config

`config/agents.json` · `docs/multi-agent.md` · `docs/providers.md`
