# PMXTrader multi-agent system

Specialized roles instead of one agent doing research + execution + MCP soup.

## Roles

| Role | Job | Providers (pick one per session) |
|------|-----|----------------------------------|
| **Scout** | Research, PH compare, thesis, write brief | Grok, Claude, OpenAI, Cursor, Codex, Hermes |
| **Trader** | Read **approved** brief → max 2 `pmxt` calls → order command | OpenAI, Cursor, Codex, Hermes |
| **Monitor** | (Future) PH WebSocket alerts | Background script |
| **You** | Approve brief, run or confirm orders | Terminal |

Config: `config/agents.json`

## Quick start

```bash
# 1. Scout session (research chat)
./pmx scout grok
./scripts/new-brief.sh fed-rate-june

# 2. Scout fills briefs/active/... — you set approved: true

# 3. Trader session (separate chat — no PH, no MCP)
./pmx trader openai briefs/active/2026-06-19-fed-rate-june.md

# 4. You paste/run the pmxt command
```

Add API keys to `pmxt/.env`, run `./scripts/setup-hermes.sh`. See `docs/providers.md`.

## Provider routing

| Provider | Best for | Command |
|----------|----------|---------|
| **Grok/xAI** | Fast Scout scans | `./pmx scout grok` |
| **Claude API** | Deep Scout briefs | `./pmx scout claude` |
| **OpenAI API** | Cheap Trader prep | `./pmx trader openai BRIEF.md` |
| **Cursor** | Rules + skills in `.cursor/` | `./pmx scout cursor` |
| **Codex** | Structured output, scripts | `./scripts/agent-run.sh scout codex` |
| **Hermes** | OAuth default / tool-calling | `./scripts/agent-run.sh scout hermes` |

Install Hermes project skills once: `./scripts/install-hermes-skills.sh`

## Handoff rule

Scout **writes** `briefs/active/*.md`. Trader **reads only** briefs with `approved: true`. Never combine Scout + Trader tools in one session.

## Prompts

- `scout/PROMPT.md` — injected into provider CLIs
- `trader/PROMPT.md` — strict execution lane
