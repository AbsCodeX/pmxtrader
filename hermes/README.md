# Hermes integration (pmxtrader)

Hermes runs Scout and Trader agents with **terminal `./pmx` commands** (not PMXT trading MCP) so Grok/xAI works reliably.

## One-time setup

```bash
./scripts/setup-hermes.sh          # recommended — Grok-safe defaults
./scripts/setup-hermes.sh --with-mcp   # Claude/Codex only — NOT Grok
./scripts/check-providers.sh
```

This will:

1. Sync LLM keys from `pmxt/.env` → `~/.hermes/.env`
2. **Disable** PMXT trading MCP (Grok schema errors)
3. **Enable** Polymarket US docs MCP (read-only, Grok-safe)
4. Link skills into `~/.hermes/skills/prediction-markets/`
5. Create bundles `/pmxtrader-scout` and `/pmxtrader-trader`

## Installed Hermes skills

| Skill | Role | Purpose |
|-------|------|---------|
| `pmxtrader-commands` | Both | Full `./pmx` reference + tool routing |
| `pmxtrader-scout` | Scout | Research lane — no orders |
| `pmxtrader-trader` | Trader | Execution lane — approved brief only |
| `pmxtrader-telegram` | Telegram | Mobile plain-language + button flows |
| `multi-agent-handoff` | Both | Brief workflow + approval gate |

Source: `hermes/skills/` · Install: `./scripts/install-hermes-skills.sh`

## Which tool agents should use

| Task | Use | Do NOT use |
|------|-----|------------|
| Kalshi analysis | Terminal `./pmx link`, `./pmx quote` | PMXT MCP (Grok) |
| Poly US quote/research | Terminal `./pmx poly quote`, `./pmx poly link` | — |
| Poly US API field lookup | MCP `polymarket_us_docs` | PMXT MCP for orders |
| Cross-venue odds (pre-trade) | Terminal `./pmx compare url` | During live Trader session |
| Kalshi live order | Terminal `./pmx trade` (human confirms) | Auto order without confirm |
| Poly US live order | Terminal `./pmx poly trade/sell/close` | Auto order without confirm |
| Account health | Terminal `./pmx status`, `./pmx warm` | — |

Canonical reference: **`docs/commands.md`**

## Scout bundle (`/pmxtrader-scout`)

**May:** `./pmx link`, `./pmx poly quote`, `./pmx compare`, `./pmx brief`, `./pmx poly markets`, Poly US docs MCP  
**Must not:** `./pmx trade`, `./pmx poly trade`, any live orders

```bash
./pmx scout grok
# or:
hermes chat --cli -t no_mcp
/pmxtrader-scout
```

## Trader bundle (`/pmxtrader-trader`)

**Requires:** brief with `approved: true`  
**May:** `./pmx status`, `./pmx quote`, `./pmx trade`, `./pmx poly trade/sell/close` (present command — human runs)  
**Must not:** PH compare, re-research, PMXT MCP during live session  
**Max:** 2 preparatory CLI calls before presenting order command

```bash
./pmx trader openai briefs/active/YOUR-BRIEF.md
# or:
/pmxtrader-trader
```

## Telegram bot (`./pmx telegram`)

Mobile Hermes control with inline buttons (brief approve, queue trade, Execute YES).

```bash
# pmxt/.env: TELEGRAM_BOT_TOKEN + TELEGRAM_ALLOWED_CHAT_IDS
./scripts/setup-hermes.sh
pip install -r requirements-telegram.txt
./pmx activate-live --bot
```

Full guide: **`docs/telegram-integration.md`**

## MCP policy

| MCP | URL / type | Trading? | Grok? | Default |
|-----|------------|----------|-------|---------|
| Polymarket US docs | `https://docs.polymarket.us/mcp` | ❌ docs only | ✅ | **ON** |
| PMXT (`@pmxt/mcp`) | stdio | ✅ multi-venue | ❌ schema errors | **OFF** |

Cursor: `.cursor/mcp.json` includes Poly US docs MCP.

## LLM routing

Add keys to `pmxt/.env`, run `./scripts/setup-hermes.sh`. Defaults in `config/providers.json`:

| Role | Command | Model hint |
|------|---------|------------|
| Scout fast | `./pmx scout grok` | grok-4.20 non-reasoning |
| Scout deep | `./pmx scout claude` | claude-sonnet |
| Trader | `./pmx trader openai BRIEF.md` | gpt-4o-mini |

Full guide: `docs/providers.md`

## Grok + PMXT MCP incompatibility

Grok/xAI rejects PMXT MCP tool schemas (HTTP 400). Scout uses **terminal** `./pmx` instead. Do not enable `--with-mcp` when using Grok.

## Re-run after changes

```bash
./scripts/setup-hermes.sh
hermes skills list | rg pmxtrader
hermes mcp list
hermes bundles list
```

## Related docs

- `docs/commands.md` — all `./pmx` shortcuts
- `docs/multi-agent.md` — Scout/Trader workflow
- `docs/polymarket-us-integration.md` — Poly US keys + retail API
- `docs/kalshi-integration.md` — Kalshi scripts
- `config/agents.json` — role constraints
