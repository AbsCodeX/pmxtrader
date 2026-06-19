---
name: multi-agent-handoff
description: >-
  pmxtrader Scout/Trader handoff for Hermes. Scout writes briefs; human sets
  approved true; Trader outputs ./pmx commands only. Separate sessions.
---

# Multi-agent handoff (Hermes)

## Workflow

```bash
./pmx brief my-game
./pmx scout grok                    # Scout session — research only
# Scout writes briefs/active/DATE-my-game.md
# Human sets approved: true in frontmatter
./pmx trader openai briefs/active/DATE-my-game.md
# Trader outputs ./pmx trade or ./pmx poly trade — human runs it
```

## Venue in brief

| Brief says | Scout uses | Trader uses |
|------------|------------|-------------|
| Kalshi | `./pmx link`, `./pmx quote` | `./pmx trade` |
| Polymarket US | `./pmx poly quote`, `./pmx poly link` | `./pmx poly trade/sell/close` |

## Hermes bundles

| Bundle | Skills |
|--------|--------|
| `/pmxtrader-scout` | pmxtrader-scout, pmxtrader-commands, multi-agent-handoff |
| `/pmxtrader-trader` | pmxtrader-trader, pmxtrader-commands, multi-agent-handoff |

Install: `./scripts/setup-hermes.sh` · `./scripts/install-hermes-skills.sh`

Config: `config/agents.json` · Commands: `docs/commands.md` · Providers: `docs/providers.md`
