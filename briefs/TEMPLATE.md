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
---

# Trade brief: TITLE

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

**Edge (manual +EV):** your probability ___ vs ask ___ → edge per contract ___

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

## Thesis (1–3 sentences)


## Trade proposal

- **Venue:** kalshi / polymarket_us
- **Side:** buy / sell
- **Outcome / side:** long / short
- **Type:** limit / market
- **Price:**
- **Size (contracts):**
- **Max risk ($):**

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

Full reference: `docs/commands.md`

## Scout notes

- Data sources used:
- Risks / unknowns:

## Human approval

- [ ] Evaluation snapshot reviewed
- [ ] I approve this trade (`approved: true` above)
