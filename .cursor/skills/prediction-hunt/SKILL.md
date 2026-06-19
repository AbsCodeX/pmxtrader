---
name: prediction-hunt
description: >-
  Prediction Hunt cross-platform odds comparison for pmxtrader. Use for pre-trade
  research (sports slate, URL matching, search) before executing on PMXT. Not for
  live in-game order execution.
---

# Prediction Hunt (research only)

## Setup

Add to `pmxt/.env`:

```
PREDICTION_HUNT_API_KEY=pmx_...
PREDICTION_HUNT_API_URL=https://www.predictionhunt.com/api/v2
```

Free key: [predictionhunt.com/api/docs](https://www.predictionhunt.com/api/docs)

## Commands

```bash
./scripts/ph-sports-compare.sh slate nba              # today's NBA slate
./scripts/ph-sports-compare.sh slate ucl 2026-06-19   # league + date
./scripts/ph-sports-compare.sh url https://kalshi.com/markets/...
./scripts/ph-sports-compare.sh search "world cup"
./scripts/ph-sports-compare.sh slate nba --json       # raw API response
```

## Workflow

1. **Pre-game:** PH compare → pick cheapest venue
2. **In-game:** `pmxt kalshi event --event-id ...` → `order:create`

Do not use PH scripts or MCP during live execution.

## API endpoints used

| Script command | PH endpoint |
|----------------|-------------|
| `slate` | `GET /v2/matching-markets/sports` |
| `url` | `GET /v2/matching-markets/url` |
| `search` | `GET /v2/search` |

## References

- [Starter scripts](https://www.predictionhunt.com/api/docs/starter-scripts)
- [Sports matching API](https://www.predictionhunt.com/api/docs/v2/matching-markets-sports)
- `.cursor/skills/pmxt-kalshi-trading/` — execution playbook
