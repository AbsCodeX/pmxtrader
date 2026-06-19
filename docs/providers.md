# LLM provider setup

Wire xAI, Claude, and OpenAI API credits into pmxtrader agents via Hermes.

## 1. Add keys to `pmxt/.env`

```bash
# Copy from each provider dashboard — never commit real keys
XAI_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

You already have **Grok via Hermes OAuth** (`xai-oauth`). `XAI_API_KEY` is optional extra pay-as-you-go credit.

## 2. Sync to Hermes

```bash
./scripts/setup-hermes.sh
# or just re-sync keys:
python3 scripts/sync-hermes-env.py ~/.hermes/.env pmxt/.env "$(python3 -c "import json;print(json.load(open('$HOME/.pmxt/cli-auth.json'))['pmxtApiKey'])")"
```

## 3. Verify

```bash
./scripts/check-providers.sh
```

## Recommended routing (~$30–50 credit each)

| Role | Provider | Command | Model (default) | Why |
|------|----------|---------|-----------------|-----|
| **Scout** fast | Grok/xAI | `./scripts/agent-run.sh scout grok` | `grok-4.20-0309-non-reasoning` | Quick scans, cheap |
| **Scout** deep | Claude | `./scripts/agent-run.sh scout claude` | `claude-sonnet-4-6` | Better briefs |
| **Trader** | OpenAI | `./scripts/agent-run.sh trader openai BRIEF.md` | `gpt-4o-mini` | Cheap command prep |
| **Trader** | Codex | `./scripts/agent-run.sh trader codex BRIEF.md` | (Codex CLI) | If you use Codex sub |
| **Either** | Cursor | `./scripts/agent-run.sh scout cursor` | (your plan) | Best rules integration |
| **Default Hermes** | auto | `./scripts/agent-run.sh scout hermes` | from `~/.hermes/config.yaml` | Your Grok OAuth today |

Change models in `config/providers.json`.

## Plain-language shortcuts

```bash
./pmx scout grok
./pmx scout claude
./pmx trader openai briefs/active/my-game.md
```

## Budget tips

- **Scout before kickoff** — one deep Claude pass, then Grok for quick updates
- **Trader** — OpenAI mini is enough; it only formats `./pmx trade` commands
- **Don't** loop LLMs on prices — use `./pmx quote` (free aside from sidecar)
- **Don't** enable PMXT MCP on Grok — use terminal `./pmx` instead
- Optional MCP for Claude only: `./scripts/setup-hermes.sh --with-mcp`

## Hermes provider names

| pmxtrader | Hermes `--provider` | Env var |
|-----------|----------------------|---------|
| grok | `xai` or `xai-oauth` | `XAI_API_KEY` |
| claude | `anthropic` | `ANTHROPIC_API_KEY` |
| openai | `openai-api` | `OPENAI_API_KEY` |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Missing OPENAI_API_KEY` | Add to `pmxt/.env`, run `./scripts/setup-hermes.sh` |
| Grok HTTP 400 with MCP | Use `-t no_mcp` (default in agent-run) |
| Claude falls back to CLI | Means no `ANTHROPIC_API_KEY` in Hermes env |
| Wrong model | Edit `config/providers.json` or `hermes model` |

See also: `hermes/README.md`, `docs/multi-agent.md`, `config/agents.json`
