# Monitor (periodic snapshots)

Background price snapshots for Scout — not an interactive LLM role.

## Use today

```bash
# Single snapshot → briefs/alerts/latest.json
./scripts/pmxt-monitor.sh --event-id EVENT --outcome-label USA --once

# Poll every 30s (Ctrl+C to stop)
./scripts/pmxt-monitor.sh --event-id EVENT --outcome-label USA --interval 30
```

For **live** orderbook/trades during a session, prefer `./scripts/pmxt-watch.sh` (Kalshi WebSocket via PMXT).

After Trader places an order, stream **your fills** (authenticated Kalshi WS, not PMXT):

```bash
./scripts/pmxt-watch-fills.sh --alert-file briefs/alerts/fills.jsonl
./scripts/pmxt-watch.sh fills OUTCOME_ID --alert-file briefs/alerts/fills.jsonl
```

Scout reads `briefs/alerts/latest.json` or watch output when updating briefs. Trader never subscribes to streams.

See [`docs/kalshi-integration.md`](../../../docs/kalshi-integration.md) for Kalshi API coverage.

## Not used

Prediction Hunt WebSocket (paid Dev/Pro tier) — we use free PH REST + PMXT streams instead.
