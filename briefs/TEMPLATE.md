---
id: YYYY-MM-DD-slug
created: YYYY-MM-DDTHH:MM:SSZ
approved: false
event_id:
market_id:
outcome_id:
venue: kalshi
scout_provider: grok
---

# Trade brief: TITLE

## Market

- **Event ID:**
- **Kalshi URL:**
- **Resolution / rules note:**

## Evaluation snapshot (required before approval)

Run:

```bash
./scripts/pmxt-eval.sh --event-id EVENT_ID --outcome-label OUTCOME --amount SIZE --balance --json
# optional cross-venue (PMXT Router, free): --router-url KALSHI_URL
```

| Field | Value |
|-------|-------|
| Outcome ID | |
| Last / mid | |
| Best bid | |
| Best ask | |
| Book depth (top 5) | bid= / ask= |
| Est. fill price (size N) | |
| Available balance | |
| 24h price change | |

**Edge (manual +EV):** your probability ___ vs ask ___ → edge per contract ___

**Kalshi orderbook note:** Kalshi shows yes/no bids; see [orderbook docs](https://docs.kalshi.com/getting_started/orderbook_responses).

## Cross-venue prices (optional — PH sports slate or PMXT Router)

| Platform | Outcome | Bid | Ask | Last |
|----------|---------|-----|-----|------|
| Kalshi   |         |     |     |      |
| Other    |         |     |     |      |

**Best venue for this trade:**

PH free: `ph-sports-compare.sh slate` (sports). Cross-venue URL: use PMXT Router in eval, not PH url (10/mo limit).

## Thesis (1–3 sentences)


## Trade proposal

- **Side:** buy / sell
- **Outcome:**
- **Type:** limit / market
- **Price:**
- **Size (contracts):**
- **Max risk ($):**

## Live monitor (optional during session)

```bash
./scripts/pmxt-eval.sh --event-id EVENT_ID --outcome-label OUTCOME --amount SIZE --balance --json
./scripts/pmxt-watch.sh orderbook OUTCOME_ID
./scripts/pmxt-watch-fills.sh --market-ticker OUTCOME_ID --alert-file briefs/alerts/fills.jsonl
# or poll: ./scripts/pmxt-monitor.sh --event-id EVENT --outcome-id OUTCOME_ID --interval 30
```

Alerts: `briefs/alerts/latest.json` (price snapshots), `briefs/alerts/fills.jsonl` (your fills after trade)

## Commands for Trader (Scout drafts; Trader validates)

```bash
pmxt kalshi event --event-id EVENT_ID --local --json
pmxt kalshi balance --local --json
# pmxt kalshi order:create --local --market-id ... --outcome-id ... --side buy --type limit --price 0.04 --amount 1 --json
```

## Scout notes

- Data sources used:
- Risks / unknowns:

## Human approval

- [ ] Evaluation snapshot reviewed
- [ ] I approve this trade (`approved: true` above)
