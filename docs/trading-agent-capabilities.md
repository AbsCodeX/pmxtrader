# Trading agent capabilities

Hermes agents **cannot** rely on PMXT MCP (Grok schema errors) or `./pmx poly markets` (often empty). All capabilities below use **terminal `./pmx`** — safe for Scout/Trader bundles with `-t no_mcp`.

## Capability map

| Capability | Scout | Trader | Command / module |
|------------|-------|--------|------------------|
| **Market discovery** | ✓ | read brief | `./pmx link URL …` · `./pmx agent discover URL` |
| **Market rules** | ✓ | read brief | Paste from venue UI; `./pmx link` may include Resolution line |
| **Live order book** | ✓ | ✓ (max 2 calls) | `./pmx quote` · `./pmx poly quote` · link analyzer |
| **Fair value estimate** | ✓ | read brief | Scout sets `fair_value_prob` in brief; edge = fair − ask |
| **Mispricing detection** | ✓ | read brief | Compare edge to category threshold (see playbooks) |
| **News / data sources** | ✓ | — | External sources listed in brief — **not** LLM-invented prices |
| **Trade recommendation** | ✓ | validate | Brief trade proposal + draft `./pmx` commands |
| **Confidence scoring** | ✓ | read brief | `confidence:` frontmatter + `score_confidence()` heuristic |
| **Trade reasoning** | ✓ | read brief | Thesis section |
| **Position tracking** | ✓ | ✓ | `./pmx positions` · `./pmx poly positions` · `./pmx agent portfolio` |
| **P&L tracking** | ✓ | ✓ | Unrealized from position JSON when venue returns it |
| **Exposure tracking** | ✓ | ✓ | Open count + notional estimate in portfolio snapshot |

## CLI (for Hermes terminal tool)

```bash
./pmx agent snapshot      # manifest + portfolio JSON
./pmx agent portfolio     # balances, positions, P&L, exposure
./pmx agent discover 'https://kalshi.com/markets/...'
./pmx scan poly-global "fed" --limit 10 --book   # Gamma/CLOB research (global)
./pmx scan poly-us "nfl" --limit 10             # US retail search (tradable)
./pmx scan verify-us MARKET-SLUG                # confirm US slug before trade
./pmx scan kalshi-btc --horizon all --limit 10  # BTC 15m + hourly on Kalshi
```

Python module: `apps/bridge/trading_agent.py`

## Hermes limitations (workarounds)

| Limitation | Workaround |
|------------|------------|
| PMXT MCP breaks Grok | Terminal `./pmx` only; MCP off in `setup-hermes.sh` |
| `./pmx poly markets` → `[]` | `./pmx scan poly-global QUERY` (Gamma) · paginated `./pmx scan poly-us` · slug verify |
| Short-term BTC discovery | `./pmx scan kalshi-btc --horizon 15m\|1h\|all` (public Kalshi API) |
| No live order execution in Hermes | Trader outputs command; human runs or confirms |
| No news API in repo | Scout cites BLS/Fed/venue pages in brief |
| No portfolio exposure cap in code | Brief `max risk ($)` + human discipline |

## Brief handoff

1. Scout runs discovery + orderbook + portfolio context
2. Scout fills `briefs/TEMPLATE.md` capability checklist + `confidence` / `fair_value_prob`
3. Human sets `approved: true`
4. Trader validates quote (≤2 prep calls) and presents exact `./pmx` command

See also: `docs/multi-agent.md`, `hermes/README.md`, `apps/agents/scout/PROMPT.md`
