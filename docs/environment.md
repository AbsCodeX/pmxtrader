# Environment variables

Last reviewed: **2026-06-19** (Batch K — see `reviews/2026-06-19/documentation-review.md`).

Secrets live in **`pmxt/.env`** (gitignored). Policy JSON lives in **`config/`** (committed, no keys). Operator overrides can be exported in the shell.

Template: **`pmxt/.env.example`**

---

## Venue credentials (`pmxt/.env`)

| Variable | Venue | Required for |
|----------|-------|--------------|
| `KALSHI_API_KEY` | Kalshi | Balance, quotes, live orders |
| `KALSHI_PRIVATE_KEY` | Kalshi | RSA key (base64 or file path) |
| `POLYMARKET_US_KEY_ID` | Polymarket US | Retail CFTC venue |
| `POLYMARKET_US_SECRET_KEY` | Polymarket US | Retail CFTC venue |

Other PMXT venues (Polymarket global, Limitless, etc.) are documented in `pmxt/.env.example` but are **not** wired into pmxtrader `./pmx` shortcuts today.

| Setup guide | Path |
|-------------|------|
| Kalshi | `pmxt/core/docs/SETUP_KALSHI.md` |
| Polymarket US | `pmxt/core/docs/SETUP_POLYMARKET_US.md` |
| pmxtrader Kalshi notes | `docs/kalshi-integration.md` |
| pmxtrader Poly US notes | `docs/polymarket-us-integration.md` |

After editing `.env`, restart the sidecar: `./pmx warm` or `./scripts/pmxt-server.sh restart`.

---

## LLM agents (`pmxt/.env` → synced to Hermes)

| Variable | Used by | Notes |
|----------|---------|-------|
| `XAI_API_KEY` | `./pmx scout grok` | Optional if Grok OAuth in `~/.hermes/config.yaml` |
| `ANTHROPIC_API_KEY` | `./pmx scout claude` | |
| `OPENAI_API_KEY` | `./pmx trader openai` | |

Sync: `./scripts/setup-hermes.sh` · Verify: `./scripts/check-providers.sh` · Routing: `docs/providers.md`

---

## Research (optional)

| Variable | Purpose |
|----------|---------|
| `PREDICTION_HUNT_API_KEY` | Cross-venue odds comparison — **research only**, not execution |
| `PREDICTION_HUNT_API_URL` | Default `https://www.predictionhunt.com/api/v2` |

---

## Trading safety (shell env)

These are **not** secrets. **`scripts/pmxt-env.sh` sets safe defaults** when sourced (via `./pmx`, direnv, or `pmxt-start`).

| Variable | Default | Effect |
|----------|---------|--------|
| `PMX_READ_ONLY` | **`1` (read-only)** | Blocks all live trades (even if kill switch is OFF) |
| `PMX_MAX_TRADE_CONTRACTS` | **`10`** | Rejects trades where size exceeds N |
| `PMX_DRY_RUN=1` | unset | Trade scripts log intent without `order:create` |
| `PMX_PREFLIGHT=1` | **`1` (on)** | Live trade scripts require reachable sidecar; set `0` to skip |
| `PMX_TRADE_CONFIRM=0` | **`1` (confirm)** | Skip interactive YES prompt before live orders |
| `KILL_SWITCH` file | absent | Repo-root sentinel — `./pmx stop on "reason"` creates it |
| `.pmx-live` file | absent | Created by `./pmx go-live` / `./pmx resume` — clears read-only for this repo session |

**Go live:** `./pmx go-live` (alias: `./pmx resume`) — disengages kill switch and creates `.pmx-live`.  
**Fresh session:** `./pmx session` removes `.pmx-live` and returns to read-only.  
**Manual override:** `unset PMX_READ_ONLY` or `export PMX_READ_ONLY=0` (without `.pmx-live`, next `pmxt-env` source resets to `1`).

CLI equivalents: `./pmx preflight` · `./pmx preview trade …` · `./pmx stop` · `./pmx trade … --dry-run` · `./pmx panic --dry-run` · `./pmx trade … --yes` (skip confirm)

See `reviews/2026-06-19/trading-safety-review.md`.

---

## PMXT sidecar

| Variable | Purpose |
|----------|---------|
| `PMXT_ACCESS_TOKEN` | Fix sidecar token to a known value (dev/API testing) |
| `PMXT_ALWAYS_RESTART=1` | Force sidecar restart on every SDK call |
| `LOG_LEVEL` | Sidecar log level (`debug`, `info`, `warn`, `error`) |

Sidecar state: `~/.pmxt/server.lock` (port + access token). See `AGENTS.md` for self-managed server behavior.

---

## Dashboard / cockpit

| Variable | Default | Purpose |
|----------|---------|---------|
| `PMXT_DASHBOARD_HOST` | `127.0.0.1` | Bind address |
| `PMXT_DASHBOARD_PORT` | `8765` | HTTP port |
| `PMXT_DASHBOARD_INSECURE_BIND=1` | unset | Allow non-loopback bind (discouraged) |
| `PMXT_DASHBOARD_TOKEN` | auto-generated | CSRF token injected into dashboard HTML |

---

## Operator / paths

| Variable | Purpose |
|----------|---------|
| `PMXTRADER_ROOT` | Repo root (set by direnv / `pmx-global.zsh`) |
| `PMXT_DIR` | Path to `pmxt/` subtree (usually `$PMXTRADER_ROOT/pmxt`) |
| `PMXT_CLI_BIN` | `pmxt` on PATH or vendored fallback |
| `PMXT_CLI_MODE` | `global` or `vendored` |
| `PMXT_TERMINAL` | Set to `iterm` to prefer iTerm over Terminal.app |

---

## Hosted PMXT (optional)

| Location | Variable |
|----------|----------|
| `~/.pmxt/cli-auth.json` | `pmxtApiKey` — used by Hermes sync and hosted CLI |
| Hermes env | `PMXT_API_KEY` — copied from cli-auth by `setup-hermes.sh` |

Get a hosted key: [pmxt.dev/dashboard](https://pmxt.dev/dashboard)
