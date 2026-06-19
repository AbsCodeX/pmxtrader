---
id: 2026-06-19-usa-aus
created: 2026-06-19T12:00:00Z
approved: false
event_id: KXWCGAME-26JUN19USAAUS
market_id:
outcome_id:
venue: kalshi
scout_provider: grok
---

# Trade brief: USA vs Australia (World Cup)

## Market

- **Event ID:** KXWCGAME-26JUN19USAAUS
- **Kalshi URL:** https://kalshi.com/markets/kxwcgame/world-cup-game
- **Resolution / rules note:** Match winner market; check Kalshi contract terms.

## Cross-venue prices (Scout — run PH before fill)

```bash
./scripts/ph-sports-compare.sh url https://kalshi.com/markets/kxwcgame/world-cup-game
```

| Platform | Outcome | Bid | Ask | Last |
|----------|---------|-----|-----|------|
| Kalshi   | USA     |     |     | ~0.96 |
| Kalshi   | Tie     |     |     | ~0.04 |

**Best venue for this trade:** Kalshi (only venue with balance)

## Thesis

Example only — not a recommendation. Low balance may limit to Tie/Australia longshots.

## Trade proposal

- **Side:** buy
- **Outcome:** (fill after Scout quote)
- **Type:** limit
- **Price:**
- **Size (contracts):** 1
- **Max risk ($):** 0.71

## Commands for Trader

```bash
pmxt kalshi event --event-id KXWCGAME-26JUN19USAAUS --local --json
pmxt kalshi balance --local --json
```
