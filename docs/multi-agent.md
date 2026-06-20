---
description: Scout and Trader roles, brief handoff, and Hermes bundle setup.
---

<div class="pmx-page-hero" markdown="1">

# Multi-agent workflow

<p class="pmx-page-lead">
Research and execution stay in separate sessions. Scout writes briefs; you approve them;
Trader prepares <code>./pmx</code> commands — you run live orders in Terminal.
</p>

</div>

## Architecture

??? note "Handoff diagram"
    ```mermaid
    flowchart LR
      subgraph research [Scout session]
        S[Scout agent]
        PH[./pmx compare]
        PMXTread[./pmx quote / poly quote]
        DOCS[Poly US docs MCP]
      end
      subgraph handoff [Handoff]
        B[briefs/active/*.md]
        H[Human approved: true]
      end
      subgraph execute [Trader session]
        T[Trader agent]
        CLI[./pmx trade / poly trade]
      end
      S --> B --> H --> T --> CLI
    ```

---

## Roles

Policy: `config/agents.json` · Skills: `apps/agents/README.md` · Tool routing: [Command reference](commands.md#which-tool-to-use-agents)

| Role | Venues | Tools |
|------|--------|-------|
| **Scout** | Kalshi + Poly US research | `./pmx link`, `./pmx poly quote`, `./pmx compare`, Poly US docs MCP |
| **Trader** | Kalshi or Poly US from brief | `./pmx trade` or `./pmx poly trade/sell/close` |
| **Human** | Both | Approve brief, confirm every order |

---

## Hermes setup

```bash
./scripts/setup-hermes.sh
./scripts/install-hermes-skills.sh   # included in setup
```

| Item | Value |
|------|-------|
| Skills | `pmxtrader-scout`, `pmxtrader-trader`, `pmxtrader-commands`, `multi-agent-handoff` |
| Bundles | `/pmxtrader-scout`, `/pmxtrader-trader` |
| Policy | Terminal `./pmx` only (`-t no_mcp`); Poly US docs MCP on; PMXT trading MCP off |

Details: [hermes/README.md](https://github.com/AbsCodeX/pmxtrader/blob/main/hermes/README.md)

---

## Provider matrix

| Provider | Scout | Trader | Notes |
|----------|-------|--------|-------|
| Grok/xAI | Yes | No | `./pmx scout grok` |
| Claude API | Yes | Brief-only | `./pmx scout claude` |
| OpenAI API | Yes | Yes | `./pmx trader openai BRIEF.md` |
| Cursor | Yes | Yes | `./pmx scout cursor` |
| Hermes | Yes | Yes | `./scripts/agent-run.sh scout hermes` |

Keys: `pmxt/.env` → `./scripts/setup-hermes.sh` → `./scripts/check-providers.sh`  
Routing details: [LLM providers](providers.md)

---

## Daily workflow

```bash
source scripts/pmxt-env.sh
./scripts/new-brief.sh fed-june
./pmx scout grok
# Scout fills brief; set approved: true and venue (Kalshi or Polymarket US)
./pmx trader openai briefs/active/2026-06-19-fed-june.md
# Human confirms and runs ./pmx trade or ./pmx poly trade
```

---

## Discipline

| Do not | Why |
|--------|-----|
| Combine PMXT MCP + PH + execution in one chat | Slow, unsafe tool overlap |
| Let Trader re-run `./pmx compare` or docs MCP | Trader lane is execution prep only |
| Auto-run `./pmx trade` without confirmation | Real money; human gate is intentional |

---

## Roadmap: Monitor role

PH WebSocket daemon → `briefs/alerts.json` → Scout reads alerts. See `apps/agents/monitor/README.md`.
