# PMXTrader multi-agent system

Specialized roles instead of one agent doing research + execution + MCP soup.

## Roles

| Role | Job | Providers (pick one per session) |
|------|-----|-----------------------------------|
| **Scout** | Research, compare, thesis, write brief | Grok, Claude, OpenAI, Cursor, Codex, Hermes |
| **Trader** | Read **approved** brief → max 2 prep calls → order command | OpenAI, Cursor, Codex, Hermes |
| **Monitor** | (Future) PH WebSocket alerts | Background script |
| **You** | Approve brief, run or confirm orders | Terminal |

Config: `config/agents.json` · Commands: **`docs/commands.md`**

## Venues

| Venue | Scout | Trader |
|-------|-------|--------|
| **Kalshi** | `./pmx link`, `./pmx quote`, `./pmx compare` | `./pmx trade` |
| **Polymarket US** | `./pmx poly quote`, `./pmx poly link`, Poly US docs MCP | `./pmx poly trade/sell/close` |

## Quick start

```bash
./scripts/setup-hermes.sh
./scripts/new-brief.sh fed-rate-june
./pmx scout grok
# Scout fills briefs/active/... — set approved: true and venue
./pmx trader openai briefs/active/2026-06-19-fed-rate-june.md
# Human confirms and runs ./pmx trade or ./pmx poly trade
```

## Hermes skills (auto-installed by setup)

| Skill | Role |
|-------|------|
| `pmxtrader-commands` | Full `./pmx` reference + tool routing |
| `pmxtrader-scout` | Research lane |
| `pmxtrader-trader` | Execution lane |
| `multi-agent-handoff` | Brief approval workflow |

Bundles: `/pmxtrader-scout` · `/pmxtrader-trader`

## Handoff rule

Scout **writes** `briefs/active/*.md`. Trader **reads only** briefs with `approved: true`. Never combine Scout + Trader tools in one session.

## Prompts

- `scout/PROMPT.md` — injected into provider CLIs
- `trader/PROMPT.md` — strict execution lane

See also: `hermes/README.md` · `docs/multi-agent.md`
