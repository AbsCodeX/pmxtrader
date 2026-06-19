# pmxtrader

Prediction market trading platform with PMXT, multi-agent workflows, and terminal-first tooling.

## Overview

`pmxtrader` wraps [PMXT](https://www.pmxt.dev/) with plain-language `./pmx` commands for **Kalshi** and **Polymarket US (retail)**, Scout/Trader agents, and Hermes integration. Real-money trading uses venue API keys in `pmxt/.env` — never committed.

## Quick start

### Option A — direnv + global commands (recommended)

```bash
./scripts/setup-direnv.sh       # once: direnv hook + pmx / pmxt-* in ~/.zshrc
# restart terminal, then from anywhere:
pmx cockpit                     # GoAccess-style terminal dashboard (stats, watchlist, access log)
pmx dashboard                   # browser command center
pmxt-terminal                   # opens macOS Terminal + session → cockpit
pmx balance
```

Inside the repo (direnv also loads aliases like `money`, `halt`):

```bash
pmxt-start                      # bootstrap sidecar + status in this shell
pmx dashboard                   # same as from anywhere
open index.html                 # shortcuts only (offline copy mode)
pmx help
```

Manual setup (if you skip the installer):

```bash
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
echo 'export PMXTRADER_ROOT=~/pmxtrader' >> ~/.zshrc
echo 'source ~/pmxtrader/scripts/pmx-global.zsh' >> ~/.zshrc
cd ~/pmxtrader && direnv allow
```

### First-time build

```bash
./scripts/setup-dev.sh          # CLI, build PMXT
```

### Credentials (`pmxt/.env`)

| Venue | Vars | Setup guide |
|-------|------|-------------|
| Kalshi | `KALSHI_API_KEY`, `KALSHI_PRIVATE_KEY` | `pmxt/core/docs/SETUP_KALSHI.md` |
| Polymarket US | `POLYMARKET_US_KEY_ID`, `POLYMARKET_US_SECRET_KEY` | `pmxt/core/docs/SETUP_POLYMARKET_US.md` |
| LLM agents | `XAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | `docs/providers.md` |
| Prediction Hunt (optional) | `PREDICTION_HUNT_API_KEY` | `docs/kalshi-integration.md` |

After editing `.env`, restart sidecar: `./pmx warm` or `./scripts/pmxt-server.sh restart`.

### Daily trading commands

```bash
# Kalshi
./pmx balance
./pmx link 'https://kalshi.com/markets/...' USA 1
./pmx trade MARKET OUTCOME 1

# Polymarket US
./pmx poly balance
./pmx poly quote MARKET-SLUG long
./pmx poly trade MARKET-SLUG long 1
./pmx poly sell MARKET-SLUG long 100
./pmx poly close MARKET-SLUG long
./pmx poly watch book MARKET-SLUG long --max-messages 10
```

Full reference: **[`docs/commands.md`](docs/commands.md)**

## Multi-agent workflow

Separate **research** (Scout) from **execution** (Trader). Human approves every live order.

```bash
./scripts/setup-hermes.sh           # once — sync keys, Hermes skills, bundles
./scripts/check-providers.sh
./scripts/new-brief.sh my-market
./pmx scout grok                    # research → briefs/active/*.md
# Set approved: true in brief frontmatter
./pmx trader openai briefs/active/DATE-my-market.md
# Human confirms, then runs ./pmx trade or ./pmx poly trade
```

| Doc | Contents |
|-----|----------|
| [`docs/commands.md`](docs/commands.md) | Complete `./pmx` reference + agent tool routing |
| [`docs/multi-agent.md`](docs/multi-agent.md) | Scout / Trader roles |
| [`docs/providers.md`](docs/providers.md) | LLM routing (grok, claude, openai) |
| [`docs/kalshi-integration.md`](docs/kalshi-integration.md) | Kalshi ↔ scripts |
| [`docs/polymarket-us-integration.md`](docs/polymarket-us-integration.md) | Poly US keys, MCP, `./pmx poly` |
| [`hermes/README.md`](hermes/README.md) | Hermes setup, MCP policy, bundles |
| [`AGENTS.md`](AGENTS.md) | Cursor Cloud + dev environment notes |

## Hermes (Grok / Claude / OpenAI agents)

```bash
./scripts/setup-hermes.sh           # Grok-safe: terminal CLI, Poly US docs MCP
./pmx scout grok                    # or: hermes chat --cli -t no_mcp → /pmxtrader-scout
./pmx trader openai briefs/active/BRIEF.md
```

- **PMXT trading MCP:** off by default (Grok schema errors). Scout/Trader use **terminal** `./pmx`.
- **Polymarket US docs MCP:** on by default (read-only API research).
- Skills installed to `~/.hermes/skills/prediction-markets/` via `./scripts/install-hermes-skills.sh`.

## Project structure

| Directory | Purpose |
|-----------|---------|
| `pmxt/` | PMXT engine (sidecar, exchanges) |
| `scripts/` | `./pmx`, agents, kill switch, venue quickstarts |
| `briefs/` | Trade brief templates + active briefs |
| `config/` | `agents.json`, `providers.json` |
| `hermes/skills/` | Hermes agent skills |
| `apps/agents/` | Scout/Trader prompts |
| `docs/` | Guides and command reference |

## Safety

- Kill switch: `./pmx stop on "reason"` · `./pmx resume` · `./pmx panic`
- Pre-commit secret scanner · strict `.gitignore` for `.env`
- Trader requires `approved: true` in brief before preparing orders

## License

MIT
