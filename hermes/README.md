# Hermes integration (pmxtrader)

## Grok + PMXT MCP incompatibility

**Grok/xAI rejects PMXT MCP tool schemas** on the first message (HTTP 400):

```
Schema validation failed: unresolvable $ref '#/components/schemas/EventFilterCriteria'
```

This is an xAI validator limitation, not a bad PMXT API key. **Default setup disables pmxt MCP.**

Scout uses **terminal CLI** instead (`pmxt`, `ph-sports-compare.sh`) via Hermes `terminal` toolset.

## One-time setup

```bash
./scripts/setup-hermes.sh          # Grok-safe (MCP off)
./scripts/setup-hermes.sh --with-mcp   # Claude/Codex only — NOT Grok
```

## LLM API keys

Add pay-as-you-go keys to `pmxt/.env` (see `pmxt/.env.example`):

```bash
XAI_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

Then sync:

```bash
./scripts/setup-hermes.sh
./scripts/check-providers.sh
```

Routing defaults in `config/providers.json` (budget-friendly for ~$30–50/credit):

| Role | Command | Model |
|------|---------|-------|
| Scout fast | `./pmx scout grok` | grok-4.20 non-reasoning |
| Scout deep | `./pmx scout claude` | claude-sonnet-4-6 |
| Trader | `./pmx trader openai BRIEF.md` | gpt-4o-mini |

Grok OAuth in `~/.hermes/config.yaml` works without `XAI_API_KEY`. See `docs/providers.md`.

## Usage (Grok)

```bash
cd ~/pmxtrader
./pmx scout grok
./scripts/agent-run.sh scout hermes    # Hermes default (your OAuth)
# In chat: /pmxtrader-scout

hermes chat --cli -t no_mcp            # manual session
```

## Provider guide

| Provider | pmxt MCP | PMXT access |
|----------|----------|-------------|
| **Grok (xAI)** | ❌ disabled | Terminal `pmxt` CLI |
| **Claude Code** | ⚠️ optional `--with-mcp` | MCP or terminal |
| **Codex** | ⚠️ optional `--with-mcp` | MCP or terminal |
| **Cursor** | N/A | `pmxt` CLI + rules |

## Re-run setup

```bash
./scripts/setup-hermes.sh
```

Syncs keys, recreates bundles, disables PMXT trading MCP, **enables Polymarket US docs MCP** ([docs.polymarket.us/mcp](https://docs.polymarket.us/mcp)).

## Polymarket US docs MCP

Read-only documentation search — **Grok-safe** (unlike PMXT MCP).

| MCP | URL | Trading? | Grok? |
|-----|-----|----------|-------|
| Polymarket US docs | `https://docs.polymarket.us/mcp` | ❌ docs only | ✅ |
| PMXT (`@pmxt/mcp`) | stdio | ✅ multi-venue | ❌ schema errors |

Cursor: `.cursor/mcp.json` · Hermes: `polymarket_us_docs` in config · Guide: `docs/polymarket-us-integration.md`
