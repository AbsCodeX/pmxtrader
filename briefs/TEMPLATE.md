---
id: YYYY-MM-DD-slug
created: YYYY-MM-DDTHH:MM:SSZ
approved: false
venue: kalshi
event_id:
market_id:
market_slug:
outcome_id:
outcome_side: long
scout_provider: grok
confidence: 0.0
fair_value_prob:
edge_pct:
---

# Trade brief: TITLE

## Agent capability checklist

Run before approval (Hermes uses terminal — no PMXT MCP on Grok):

```bash
./pmx agent discover 'MARKET_URL'
./pmx scan poly-global "QUERY" --limit 10
./pmx scan poly-us "QUERY" --limit 10
./pmx scan verify-us SLUG
./pmx scan kalshi-btc --horizon all --limit 10
./pmx watchlist scan
./pmx propose --fair 0.62 --ask 0.50 --event EVENT --outcome YES
./pmx agent portfolio
./pmx agent snapshot
```

| Capability | Status | Notes |
|------------|--------|-------|
| Market discovery | ☐ | URL → event/slug via `./pmx link` |
| Market rules | ☐ | Paste venue rules; link may include Resolution line |
| Live order book | ☐ | bid/ask/mid from link or quote |
| Fair value estimate | ☐ | Your prob vs ask → edge |
| Mispricing (+EV) | ☐ | Edge ≥ category threshold? |
| Data sources checked | ☐ | List primary sources (not LLM guesses) |
| Trade recommendation | ☐ | `./pmx propose` or fill proposal section below |
| Confidence score | ☐ | 0–1 heuristic in frontmatter |
| Trade reasoning | ☐ | Thesis below |
| Positions | ☐ | `./pmx positions` / `poly positions` |
| P&L | ☐ | Unrealized from position JSON if present |
| Exposure | ☐ | Open count + notional vs max risk |

**Poly US note:** `./pmx poly markets` often returns `[]` — use known slugs or `./pmx poly link`.

## Market

- **Venue:** `kalshi` or `polymarket_us`
- **Event ID / Slug:**
- **URL:**
- **Resolution / rules note:**

## Evaluation snapshot (required before approval)

**Kalshi:**

```bash
./pmx link 'KALSHI_URL' OUTCOME 1
# or: ./pmx quote EVENT_ID OUTCOME 1
```

**Polymarket US:**

```bash
./pmx poly link 'https://polymarket.us/market/SLUG' long
# or: ./pmx poly quote SLUG long
```

| Field | Value |
|-------|-------|
| Outcome ID / side | |
| Last / mid | |
| Best bid | |
| Best ask | |
| Book depth (top 5) | bid= / ask= |
| Est. fill price (size N) | |
| Available balance | |
| 24h price change | |

**Fair value:** your probability ___ · **Ask:** ___ · **Edge:** ___ (per contract)

**Confidence:** ___ (0–1) — book depth, rules clarity, data freshness, cross-venue agree

## Cross-venue prices (optional — Scout only)

```bash
./pmx compare url URL
./pmx compare slate SPORT
```

| Platform | Outcome | Bid | Ask | Last |
|----------|---------|-----|-----|------|
| Kalshi   |         |     |     |      |
| Poly US  |         |     |     |      |
| Other    |         |     |     |      |

**Best venue for this trade:**

## Thesis / reasoning (1–3 sentences)


## Trade proposal

- **Venue:** kalshi / polymarket_us
- **Side:** buy / sell
- **Outcome / side:** long / short
- **Type:** limit / market
- **Price:**
- **Size (contracts):**
- **Max risk ($):**

## Portfolio context

```bash
./pmx agent portfolio
```

| Metric | Value |
|--------|-------|
| Kalshi cash | |
| Poly US cash | |
| Open positions | |
| Unrealized P&L | |
| Notional exposure | |

## Live monitor (optional during session)

**Kalshi:**

```bash
./pmx watch OUTCOME_ID
./pmx fills OUTCOME_ID
```

**Polymarket US:**

```bash
./pmx poly watch book SLUG long --max-messages 10
./pmx poly history SLUG --limit 20
```

## Commands for Trader (Scout drafts; Trader validates)

**Kalshi:**

```bash
./pmx status
./pmx quote EVENT OUTCOME SIZE
./pmx trade MARKET OUTCOME SIZE
```

**Polymarket US:**

```bash
./pmx status
./pmx poly quote SLUG long
./pmx poly trade SLUG long 1
./pmx poly sell SLUG long 100
./pmx poly close SLUG long
```

Full reference: `docs/commands.md` · `docs/trading-agent-capabilities.md`

## Scout notes

- Data sources used (news, official releases, compare):
- Risks / unknowns:

## Human approval

- [ ] Evaluation snapshot reviewed
- [ ] Capability checklist complete
- [ ] I approve this trade (`approved: true` above)
