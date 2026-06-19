# Polymarket US integration

Maps [Polymarket US docs](https://docs.polymarket.us/getting-started/welcome) to pmxtrader tooling.

## What Polymarket US MCP is

[docs.polymarket.us/mcp](https://docs.polymarket.us/mcp) is a **documentation MCP** (Mintlify HTTP) — not a live trading MCP.

| Tool | Purpose |
|------|---------|
| `search_polymarket_us_documentation` | Semantic search across US docs |
| `query_docs_filesystem_polymarket_us_documentation` | Read/search doc pages (`head`, `rg`, `cat` on virtual FS) |

Use it when building Polymarket US features, debugging auth, or looking up order API fields. **Execution** still goes through `pmxt polymarket_us` CLI (or future `./pmx poly-us` shortcuts).

## Cursor

Project config: `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "polymarket-us-docs": {
      "url": "https://docs.polymarket.us/mcp"
    }
  }
}
```

Reload Cursor after changes. No API key required for the docs MCP.

## Hermes

Enabled by default in `./scripts/setup-hermes.sh` (Grok-safe — docs only):

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  polymarket_us_docs:
    url: https://docs.polymarket.us/mcp
    enabled: true
```

Manual toggle:

```bash
python3 scripts/enable-hermes-polymarket-us-mcp.py enable ~/.hermes/config.yaml
python3 scripts/enable-hermes-polymarket-us-mcp.py disable ~/.hermes/config.yaml
```

**Do not confuse with PMXT MCP** (`@pmxt/mcp`) — that is multi-venue trading and breaks on Grok. Polymarket US docs MCP is fine on all providers.

## API keys → PMXT

| Portal | `pmxt/.env` |
|--------|-------------|
| Key ID | `POLYMARKET_US_KEY_ID` |
| Secret Key | `POLYMARKET_US_SECRET_KEY` |

Get keys: [polymarket.us/developer](https://polymarket.us/developer)

Setup guide: `pmxt/core/docs/SETUP_POLYMARKET_US.md`

## PMXT exchange id + `./pmx poly`

```bash
./pmx poly balance
./pmx poly quote MARKET-SLUG long
./pmx poly trade MARKET-SLUG long 1
./pmx poly trade MARKET-SLUG long 10 0.55   # limit
pmxt polymarket_us markets --limit 5 --local --json
```

Setup: `pmxt/core/docs/SETUP_POLYMARKET_US.md`

## Scout vs Trader

| Role | Polymarket US docs MCP | Live Poly US orders |
|------|------------------------|-------------------|
| **Scout** | ✅ research / integration | ❌ use Kalshi or brief only |
| **Trader** | ❌ not during live session | ✅ `./pmx poly trade` (human confirm) |

Cross-venue **research** from Kalshi links still uses Prediction Hunt / PMXT Router (often international Polymarket, not US).

## Related

- Kalshi workflow: `docs/kalshi-integration.md`
- Hermes MCP policy: `hermes/README.md`
- International Polymarket: `pmxt/core/docs/SETUP_POLYMARKET.md`
