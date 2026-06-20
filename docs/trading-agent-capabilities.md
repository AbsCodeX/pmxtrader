# Trading agent capabilities

Hermes agents **cannot** rely on PMXT MCP (Grok schema errors) or `./pmx poly markets` (often empty). All capabilities below use **terminal `./pmx`** — safe for Scout/Trader bundles with `-t no_mcp`.

## Capability map

| Capability | Scout | Trader | Command / module |
|------------|-------|--------|------------------|
| **Market discovery** | ✓ | read brief | `./pmx link URL …` · `./pmx agent discover URL` · `./pmx watchlist scan` |
| **Market rules** | ✓ | read brief | Paste from venue UI; `./pmx link` may include Resolution line |
| **Live order book** | ✓ | ✓ (max 2 calls) | `./pmx quote` · `./pmx poly quote` · link analyzer |
| **Fair value estimate** | ✓ | read brief | Scout sets `fair_value_prob` in brief; edge = fair − ask |
| **Mispricing detection** | ✓ | read brief | Compare edge to category threshold (see playbooks) |
| **News / data sources** | ✓ | — | External sources listed in brief — **not** LLM-invented prices |
| **Trade recommendation** | ✓ | validate | `./pmx propose` · `./pmx approve` · brief trade proposal + draft `./pmx` commands |
| **Risk & sizing** | ✓ | read brief | `./pmx risk check` · `./pmx risk status` · Kelly + daily loss ledger |
| **Confidence scoring** | ✓ | read brief | `confidence:` frontmatter + `score_confidence()` heuristic |
| **Trade reasoning** | ✓ | read brief | Thesis section |
| **Position tracking** | ✓ | ✓ | `./pmx positions` · `./pmx poly positions` · `./pmx agent portfolio` |
| **P&L tracking** | ✓ | ✓ | Unrealized from position JSON when venue returns it |
| **Exposure tracking** | ✓ | ✓ | Open count + notional estimate in portfolio snapshot |
| **Price alerts** | ✓ | — | `./pmx alert scan` · `./pmx watchlist alert` (watchlist vs snapshots) |

## CLI (for Hermes terminal tool)

```bash
./pmx agent snapshot      # manifest + portfolio + credential_status JSON
./pmx agent doctor        # credential + sidecar diagnostics (Hermes first step)
./pmx agent portfolio     # balances, positions, P&L, exposure
./pmx agent discover 'https://kalshi.com/markets/...'
./pmx scan poly-global "fed" --limit 10 --book   # Gamma/CLOB research (global)
./pmx scan poly-us "nfl" --limit 10             # US retail search (tradable)
./pmx scan verify-us MARKET-SLUG                # confirm US slug before trade
./pmx scan kalshi-btc --horizon all --limit 10  # BTC 15m + hourly on Kalshi
./pmx watchlist list                            # curated markets + filters
./pmx watchlist add --url 'MARKET_URL'          # infer venue from URL
./pmx watchlist scan                            # live check + volume/liquidity filters
./pmx propose --fair 0.62 --ask 0.50 --event EVENT --outcome YES --use-portfolio
./pmx propose --url 'MARKET_URL' --fair 0.62 --markdown   # paste into brief
./pmx risk check --fair 0.62 --ask 0.50 --bankroll 500    # edge + Kelly + risk checks
./pmx risk status                                         # daily P&L ledger (set PMX_MAX_DAILY_LOSS)
./pmx approve --fair 0.62 --ask 0.50 --event EVENT --confirm YES
./pmx alert scan --threshold 0.05 --once                  # watchlist price shifts
```

Python modules: `apps/bridge/trading_agent.py` · `risk_engine.py` · `approval.py` · `price_alert.py`

## Hermes limitations (workarounds)

| Limitation | Workaround |
|------------|------------|
| PMXT MCP breaks Grok | Terminal `./pmx` only; MCP off in `setup-hermes.sh` |
| `./pmx poly markets` → `[]` | `./pmx scan poly-global QUERY` (Gamma) · paginated `./pmx scan poly-us` · slug verify · **`./pmx watchlist`** curated list |
| Balance fails / "keys not configured" | Keys in **`pmxt/.env`** (not ~/.hermes/.env). Run `./pmx agent doctor` then `./scripts/pmxt-server.sh restart` if sidecar stale |
| Read-only blocks trades not balance | `PMX_READ_ONLY=1` default — `./pmx go-live` for live orders; `./pmx balance` still needs venue keys |
| Short-term BTC discovery | `./pmx scan kalshi-btc --horizon 15m\|1h\|all` (public Kalshi API) |
| No live order execution in Hermes | Trader outputs command; human runs or confirms |
| No news API in repo | Scout cites BLS/Fed/venue pages in brief |
| No portfolio exposure cap in code | `./pmx risk check` + `PMX_MAX_PORTFOLIO_PCT` + brief `max risk ($)` |

## Brief handoff

1. Scout runs discovery + orderbook + portfolio context
2. Scout fills `briefs/TEMPLATE.md` capability checklist + `confidence` / `fair_value_prob`
3. Human sets `approved: true`
4. Trader validates quote (≤2 prep calls) and presents exact `./pmx` command

See also: `docs/multi-agent.md`, `hermes/README.md`, `apps/agents/scout/PROMPT.md`
