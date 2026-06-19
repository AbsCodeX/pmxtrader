# Polymarket US setup (pmxtrader + PMXT)

Polymarket US is a separate product from [polymarket.com](https://polymarket.com) (international CLOB).

Official docs: [docs.polymarket.us](https://docs.polymarket.us/getting-started/welcome)  
Docs MCP (read-only): [docs.polymarket.us/mcp](https://docs.polymarket.us/mcp)

## 1. Get API keys

1. Install the **Polymarket US** app and complete identity verification.
2. Open [polymarket.us/developer](https://polymarket.us/developer) (same sign-in as the app).
3. Create an API key → copy **Key ID** and **Secret Key** (secret shown once).

Auth uses Ed25519 request signing (`X-PM-Access-Key`, `X-PM-Timestamp`, `X-PM-Signature`). PMXT handles this via the `polymarket-us` SDK — you only store the keys.

Support: support@polymarket.us

## 2. Configure `pmxt/.env`

```bash
POLYMARKET_US_KEY_ID=your-key-id
POLYMARKET_US_SECRET_KEY=your-base64-secret-key
```

Do **not** use `POLYMARKET_*` (international) vars for US trading.

## 3. Verify PMXT

```bash
source scripts/pmxt-env.sh
./pmx poly markets nfl                         # public — no keys
./pmx poly quote MARKET-SLUG long              # orderbook
./pmx poly balance                             # needs keys
./pmx poly positions
```

Direct PMXT:

```bash
pmxt polymarket_us markets --limit 3 --local --json
pmxt polymarket_us balance --local --json
```

## 4. Trade via `./pmx poly` (real money)

Kill switch applies to new orders: `./pmx status` must show OFF for `trade`, `sell`, and `close`.

```bash
./pmx poly quote chiefs-super-bowl-lx long
./pmx poly trade chiefs-super-bowl-lx long 1              # market buy
./pmx poly trade chiefs-super-bowl-lx long 10 0.55         # limit @ $0.55
./pmx poly sell MARKET-SLUG long 100                       # market sell
./pmx poly close MARKET-SLUG long                          # flatten position
./pmx poly watch book MARKET-SLUG long --max-messages 10   # live book (active markets)
./pmx poly history --limit 20                              # your fills
./pmx poly link 'https://polymarket.us/market/SLUG' long
./pmx poly orders
./pmx poly cancel ORDER_ID
./pmx poly cancel-all
```

Side convention: `long` = buy YES side, `short` = buy NO side (PMXT outcome ids: `SLUG:long`, `SLUG:short`).

## 5. Docs MCP (Cursor + Hermes)

Read-only documentation search — safe for Scout, works with Grok (unlike PMXT trading MCP).

**Cursor:** project `.cursor/mcp.json` points at `https://docs.polymarket.us/mcp`

**Hermes:**

```bash
./scripts/setup-hermes.sh
# enables polymarket_us_docs MCP by default
hermes mcp list
```

Tools: `search_polymarket_us_documentation`, `query_docs_filesystem_polymarket_us_documentation`

## 6. Direct PMXT orders (advanced)

```bash
pmxt polymarket_us order:create --local \
  --market-id SLUG --outcome-id SLUG:long \
  --side buy --type market --amount 1 --json
```

See [Polymarket US API reference](https://docs.polymarket.us/api-reference/introduction).

Prefer `./pmx poly trade` — see section 4.

## International Polymarket

For `polymarket.com` (not US), see `SETUP_POLYMARKET.md` and `POLYMARKET_PRIVATE_KEY` / CLOB keys.
