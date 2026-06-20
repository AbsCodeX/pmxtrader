---
description: Kalshi API mapping, scripts, streaming, and execution paths.
---

<div class="pmx-page-hero" markdown="1">

# Kalshi integration

<p class="pmx-page-lead">
Maps official Kalshi API capabilities to pmxtrader scripts. Free streaming and evaluation — no paid Prediction Hunt required.
</p>

</div>

## Kalshi API surface (official)

| Kalshi feature | Docs | pmxtrader tool |
|----------------|------|----------------|
| Event + markets | [Get Event](https://docs.kalshi.com/api-reference/events/get-event) | `pmxt kalshi event --event-id` / `pmxt-eval.sh` |
| Orderbook (REST) | [Get Market Orderbook](https://docs.kalshi.com/api-reference/market/get-market-orderbook) | `pmxt kalshi orderbook` / `pmxt-eval.sh` |
| Orderbook (WS) | [Orderbook Updates](https://docs.kalshi.com/websockets/orderbook-updates) | `pmxt-watch.sh orderbook` |
| Ticker / last | [Market Ticker WS](https://docs.kalshi.com/websockets/market-ticker) | Included in PMXT watch streams |
| Public trades | [Public Trades WS](https://docs.kalshi.com/websockets/public-trades) | `pmxt-watch.sh trades` |
| Balance / positions | [Get Balance](https://docs.kalshi.com/api-reference/portfolio/get-balance), [Get Positions](https://docs.kalshi.com/api-reference/portfolio/get-positions) | `kalshi-quickstart.sh balance\|positions` |
| Create order (V2) | [Create Order V2](https://docs.kalshi.com/api-reference/orders/create-order-v2) | `kalshi-quickstart.sh trade` → PMXT `order:create` |
| User fills (WS) | [User Fills](https://docs.kalshi.com/websockets/user-fills) | `pmxt-watch-fills.sh` / `pmxt-watch.sh fills` |
| User orders (WS) | [User Orders](https://docs.kalshi.com/websockets/user-orders) | Not wrapped — use fills stream + REST positions |
| Rate limits | [Rate Limits](https://docs.kalshi.com/getting_started/rate_limits) | Prefer **watch** over tight polling |
| Orderbook model | [Orderbook Responses](https://docs.kalshi.com/getting_started/orderbook_responses) | Yes/no **bids** only; opposite side ask is implied (binary) |
| Fixed-point prices | [Fixed-Point Migration](https://docs.kalshi.com/getting_started/fixed_point_migration) | PMXT normalizes to decimal prices in CLI output |
| Order direction | [Order direction](https://docs.kalshi.com/getting_started/order_direction) | PMXT abstracts `outcome_side` / `book_side` |
| Fees | [Fee Rounding](https://docs.kalshi.com/getting_started/fee_rounding) | Not in `pmxt-eval.sh` — subtract from edge manually |
| Exchange status | [Get Exchange Status](https://docs.kalshi.com/api-reference/exchange/get-exchange-status) | Not wrapped — check kalshi.com if orders fail |
| Live sports stats | [Get Game Stats](https://docs.kalshi.com/api-reference/live-data/get-game-stats) | Not wrapped — Kalshi REST if needed |
| Sports discovery | [Get Filters for Sports](https://docs.kalshi.com/api-reference/search/get-filters-for-sports) | Use PH `ph-sports-compare.sh slate` or Kalshi site footer event ID |
| Cross-venue prices | N/A on Kalshi alone | PMXT Router `--hosted --include-prices` (free PMXT key) |

Kalshi recommends combining REST with WebSocket for accurate state ([Get User Data Timestamp](https://docs.kalshi.com/api-reference/exchange/get-user-data-timestamp)). Our monitor + watch scripts follow that pattern.

## Official docs checklist (what we cover vs skip)

**Covered (free, via PMXT + scripts):**

- Market data: event, orderbook REST, orderbook/trades WebSocket
- Portfolio reads: balance, positions
- Trade execution: PMXT order create (V2 path inside PMXT)
- Fill estimation: `pmxt execution-price` in `pmxt-eval.sh`
- Cross-venue: PMXT Router (not Kalshi-native)

**Intentionally not wrapped (low value or out of scope):**

- Perps / margin API ([separate product](https://docs.kalshi.com/margin))
- RFQ, block trades, order groups, subaccounts
- Historical archive endpoints ([Historical Data](https://docs.kalshi.com/getting_started/historical_data))
- FIX protocol
- Authenticated user-order WebSocket streams (use REST positions after trade; **user fills** via `pmxt-watch-fills.sh`)

**Operational notes from Kalshi:**

- WebSocket handshake requires API key auth even for public channels ([WebSocket Connection](https://docs.kalshi.com/websockets/websocket-connection)) — PMXT handles this when keys are in `pmxt/.env`.
- Server sends Ping every 10s (`heartbeat`); client must Pong ([Keep-Alive](https://docs.kalshi.com/websockets/connection-keep-alive)) — PMXT `watch:*` handles this.
- Legacy order endpoint deprecated no earlier than **May 6, 2026** — PMXT should use V2; verify on upgrade.
- Demo vs production use **different base URLs and keys** ([Demo Environment](https://docs.kalshi.com/getting_started/demo_env), [API Environments](https://docs.kalshi.com/getting_started/api_environments)) — this repo defaults to **live**.

## Scripts

### Evaluation snapshot (before approving a brief)

```bash
./pmx link 'https://kalshi.com/markets/kxwcgame/world-cup-game' USA 1
./scripts/pmxt-eval.sh --event-id KXWCGAME-26JUN19USAAUS --outcome-label USA --amount 1 --balance
./scripts/pmxt-eval.sh --event-id EVENT --router-url https://kalshi.com/markets/... --json
```

Returns: price, bid/ask, orderbook depth, estimated fill price, optional cross-venue (PMXT Router), balance.

### Live stream (in session)

```bash
# Get outcomeId first
./scripts/pmxt-eval.sh --event-id EVENT --json | jq -r .outcomeId

./scripts/pmxt-watch.sh orderbook OUTCOME_ID
./scripts/pmxt-watch.sh trades OUTCOME_ID --max-messages 50
./scripts/pmxt-watch-fills.sh --alert-file briefs/alerts/fills.jsonl
./scripts/pmxt-watch-fills.sh --market-ticker OUTCOME_ID --max-messages 5
```

### User fill stream (after Trader places order)

```bash
# All your fills (authenticated Kalshi WS — not PMXT watch:*)
./scripts/pmxt-watch-fills.sh --alert-file briefs/alerts/fills.jsonl

# Filter to one market/outcome
./scripts/pmxt-watch.sh fills OUTCOME_ID --alert-file briefs/alerts/fills.jsonl
```

### Periodic monitor (Scout background)

```bash
./scripts/pmxt-monitor.sh --event-id EVENT --outcome-label USA --interval 30
./scripts/pmxt-monitor.sh --event-id EVENT --once   # single snapshot → briefs/alerts/latest.json
```

### Kill switch and emergency stop

File sentinel at repo root (`KILL_SWITCH`, gitignored). Works even if agents hang.

```bash
./scripts/kill-switch.sh status
./scripts/kill-switch.sh on "no more live bets tonight"
./scripts/kill-switch.sh off

# Block new trades + cancel resting orders
./scripts/kill-switch.sh stop

# Also market-close all positions (type PANIC to confirm)
./scripts/kill-switch.sh stop --cash-out
./scripts/kill-switch.sh stop --dry-run --cash-out
```

| Command | Block new trades | Cancel orders | Close positions |
|---------|------------------|---------------|-----------------|
| `on` | yes | no | no |
| `stop` | yes | yes | no |
| `stop --cash-out` | yes | yes | yes |

`kalshi-quickstart.sh trade` refuses when engaged. Override path: `KILL_SWITCH_FILE`.

### Emergency exit (direct Kalshi REST)

`./scripts/kalshi-emergency-exit.py` (invoked by `./scripts/kill-switch.sh stop --cash-out`) uses **two paths**:

| Step | Path | Why |
|------|------|-----|
| Cancel resting orders | PMXT `kalshi order:cancel --local` | Same as normal tooling |
| Close open positions | **Direct** `POST /trade-api/v2/portfolio/orders` | PMXT `createOrder` cannot map reduce-only market closes with correct action/side for both YES and NO exposure |

Direct REST bypasses the PMXT sidecar throttler. The script spaces requests by **100ms** (matching PMXT’s Kalshi adapter) and retries **GET positions once** on HTTP 429/503. **POST close orders are not auto-retried** (duplicate-fill risk).

Base URL: `KALSHI_BASE_URL` or `https://external-api.kalshi.com` (see `pmxt/core/src/exchanges/kalshi/config.ts`).

## Cross-venue without PH paid tier

| Method | Cost | Limit |
|--------|------|-------|
| PH `ph-sports-compare.sh slate` | Free | Sports only, unlimited |
| PH `ph-sports-compare.sh url` | Free | **10 matched markets/month** |
| PMXT `router:market-matches --hosted` | Free (PMXT API key) | Use in `pmxt-eval.sh --router-url` |

## Not available free

- PH smart money / +EV / arb WebSocket
- PH +EV model — compute edge manually in brief: `(your_prob - ask) × size`

## Credentials

Live Kalshi: `KALSHI_API_KEY` + `KALSHI_PRIVATE_KEY` in `pmxt/.env`  
PMXT Router: `~/.pmxt/cli-auth.json` (from `pmxt auth login`)

Demo environment: [Kalshi demo](https://docs.kalshi.com/getting_started/demo_env) — separate keys; this project uses **live** by default.
