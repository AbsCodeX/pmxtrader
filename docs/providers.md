---
description: LLM provider keys, Hermes sync, model routing, and budget guidance.
---

<div class="pmx-page-hero" markdown="1">

# LLM providers

<p class="pmx-page-lead">
Wire xAI, Anthropic, and OpenAI credentials into Scout and Trader agents via Hermes.
Market prices come from <code>./pmx quote</code> — not from the LLM.
</p>

</div>

## Setup

### 1. Add keys to `pmxt/.env`

```bash
# Copy from each provider dashboard — never commit real keys
XAI_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

Grok via Hermes OAuth (`xai-oauth`) works without `XAI_API_KEY`; the key is optional pay-as-you-go credit.

### 2. Sync to Hermes

```bash
./scripts/setup-hermes.sh
```

Re-sync keys only:

```bash
python3 scripts/sync-hermes-env.py ~/.hermes/.env pmxt/.env "$(python3 -c "import json;print(json.load(open('$HOME/.pmxt/cli-auth.json'))['pmxtApiKey'])")"
```

### 3. Verify

```bash
./scripts/check-providers.sh
```

---

## Recommended routing

Typical budget: ~$30–50 credit per provider for occasional sessions.

| Role | Provider | Command | Default model | Rationale |
|------|----------|---------|---------------|-----------|
| Scout (fast) | Grok/xAI | `./pmx scout grok` | `grok-4.20-0309-non-reasoning` | Quick scans |
| Scout (deep) | Claude | `./pmx scout claude` | `claude-sonnet-4-6` | Stronger briefs |
| Trader | OpenAI | `./pmx trader openai BRIEF.md` | `gpt-4o-mini` | Command formatting |
| Trader | Codex | `./pmx trader codex BRIEF.md` | Codex CLI | If you use Codex |
| Either | Cursor | `./pmx scout cursor` | Your plan | Rules + skills in IDE |
| Default | Hermes | `./pmx scout hermes` | `~/.hermes/config.yaml` | OAuth Grok today |

Change defaults in `config/providers.json`.

---

## Plain-language shortcuts

```bash
./pmx scout grok
./pmx scout claude
./pmx trader openai briefs/active/my-game.md
```

---

## Budget discipline

| Practice | Reason |
|----------|--------|
| One deep Scout pass before kickoff | Claude for brief quality |
| Grok for in-session updates | Lower cost per refresh |
| Trader on OpenAI mini | Formats commands only |
| `./pmx quote` for prices | Sidecar reads, not LLM tokens |
| No PMXT MCP on Grok | Schema errors; use terminal `./pmx` |
| MCP for Claude only (optional) | `./scripts/setup-hermes.sh --with-mcp` |

---

## Hermes provider names

| pmxtrader | Hermes `--provider` | Env var |
|-----------|----------------------|---------|
| grok | `xai` or `xai-oauth` | `XAI_API_KEY` |
| claude | `anthropic` | `ANTHROPIC_API_KEY` |
| openai | `openai-api` | `OPENAI_API_KEY` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Missing OPENAI_API_KEY` | Add to `pmxt/.env`, run `./scripts/setup-hermes.sh` |
| Grok HTTP 400 with MCP | Use `-t no_mcp` (default in agent-run) |
| Claude falls back to CLI | No `ANTHROPIC_API_KEY` in Hermes env |
| Wrong model | Edit `config/providers.json` or `hermes model` |

---

## Related

- [Multi-agent workflow](multi-agent.md)
- [hermes/README.md](https://github.com/AbsCodeX/pmxtrader/blob/main/hermes/README.md)
- `config/agents.json`
