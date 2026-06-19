# AGENTS.md

## Cursor Cloud specific instructions

This repo (`pmxtrader`) has two layers:

- **Root `pmxtrader`** — a thin scaffold. Its *real* CI is Python‑based, defined in
  `.github/workflows/ci.yml`: a secret scanner (`scripts/pre_commit_secret_check.py`),
  `ruff check .`, and `mypy . --ignore-missing-imports`. The root `package.json`
  `build`/`lint` scripts (`tsc`, `eslint`) are early‑stage placeholders and are **not**
  functional yet (no root `.eslintrc`; the root `tsconfig` globs the vendored
  `pmxt/**` test files). Don't rely on them — use the `pmxt-core` build below.
- **`pmxt/`** — a vendored npm‑workspaces monorepo (the PMXT "ccxt for prediction
  markets" engine). This is the actual runnable application: a sidecar HTTP server
  (`pmxt-core`), a CLI (`@pmxt/cli`), and Python/TypeScript SDKs. See
  `pmxt/CONTRIBUTING.md` and `pmxt/ARCHITECTURE.md`.

### Key gotchas

- **`pmxt-mcp` and `molt-pmxt` are git submodules.** After cloning, run
  `git submodule update --init`. URLs are in `.gitmodules`.
- **`pmxt/node_modules` is committed to git** (~34k files) even though `.gitignore`
  lists it, and the committed copy contains **macOS arm64** binaries. On the x86_64
  Linux VM these don't run (e.g. esbuild/tsx fail). The startup update script runs
  `npm --prefix pmxt install`, which adds the correct `linux-x64` platform packages
  in place and fixes this. **Do not commit the resulting `node_modules` changes** —
  they are environment artifacts, not source. Only commit real source files.
- **`ruff`/`mypy` install to `~/.local/bin`, which is not on `PATH`.** Invoke them as
  `python3 -m ruff check .` and `python3 -m mypy . --ignore-missing-imports` (works
  regardless of PATH).
- **The sidecar server is self‑managing.** Any SDK call or `pmxt ... --local` CLI
  command invokes `core/bin/pmxt-ensure-server`, which will **stop a manually started
  dev server and respawn its own** (with a fresh random access token) via the lock
  file at `~/.pmxt/server.lock`. So if you start `npm run server` manually and then
  run a CLI/SDK command, your server is replaced. To call the HTTP API directly, read
  the current port and `accessToken` from `~/.pmxt/server.lock` and send the token in
  the `x-pmxt-access-token` header. Setting `PMXT_ACCESS_TOKEN` before starting the
  server fixes the token to a known value.

### Run / build / test / lint (from repo root)

Root CI checks (Python):

- Lint: `python3 -m ruff check .`
- Types: `python3 -m mypy . --ignore-missing-imports`
- Secrets: `python3 scripts/pre_commit_secret_check.py`

PMXT engine (the app):

- Build core: `npm run build --workspace=pmxt-core --prefix pmxt`
- Unit tests: `npm test --workspace=pmxt-core --prefix pmxt` (jest, ~650 tests)
- Dev server: `cd pmxt && npm run server` (tsx watch, port 3847, falls back up to
  3947 if busy). Health: `GET http://localhost:3847/health`. Data:
  `POST /api/<exchange>/<method>` with `x-pmxt-access-token`, body
  `{"args":[ ... ]}`, e.g. `POST /api/polymarket/fetchEvents {"args":[{"query":"Fed"}]}`.
- CLI: `node pmxt/sdks/cli/bin/pmxt.js <exchange> <command> --local`
  (e.g. `... polymarket markets --query Trump --limit 3 --local`).
- Full integration suite: `cd pmxt && npm test` (runs `scripts/verify-all.sh`,
  which builds core, runs jest, starts the server, and exercises the Python + TS
  SDKs end‑to‑end; needs outbound internet to public market APIs).

Read‑only market‑data reads (events/markets/orderbooks) use public venue APIs and
need **no** credentials. Trading/account methods need venue API keys — see
`pmxt/.env.example`.

### Terminal + CLI setup

One-time (or after clone):

```bash
./scripts/setup-dev.sh
```

Each new shell (or use `direnv allow` — loads `.envrc` + `pmx` aliases):

```bash
source scripts/pmxt-env.sh
# or: source scripts/pmx-aliases.sh
```

Plain-language shortcuts: `./pmx help` (same commands work as `money`, `halt`, `panic`, etc.)

This exports `PMXTRADER_ROOT`, `PMXT_DIR`, and the `pmxt_cli` helper. Prefer the
**global** `@pmxt/cli` (`pmxt` on PATH); setup installs it if missing. Vendored
fallback: `node pmxt/sdks/cli/bin/pmxt.js`.

Warm the sidecar before a trading session (~0.3s reads afterward):

```bash
./scripts/pmxt-warm.sh
# or: pmxt kalshi balance --local --json
```

Live Kalshi shortcuts (real money — keys in `pmxt/.env`):

```bash
./scripts/kalshi-quickstart.sh event KXWCGAME-26JUN19USAAUS
./scripts/kalshi-quickstart.sh eval KXWCGAME-26JUN19USAAUS USA 1
./scripts/kalshi-quickstart.sh balance
./scripts/kalshi-quickstart.sh trade MARKET_ID OUTCOME_ID 1
```

Free streaming + evaluation (no paid PH):

```bash
./scripts/pmxt-eval.sh --event-id EVENT --outcome-label USA --amount 1 --balance
./scripts/pmxt-watch.sh orderbook OUTCOME_ID
./scripts/pmxt-monitor.sh --event-id EVENT --once
./scripts/pmxt-watch-fills.sh --alert-file briefs/alerts/fills.jsonl
./scripts/kill-switch.sh status
```

Kalshi API mapping: `docs/kalshi-integration.md`

MCP (research / cross-venue only — not for in-game order execution):

```bash
./scripts/start-pmxt-mcp.sh   # requires pmxt auth login
```

Prediction Hunt cross-platform odds (pre-trade research only — not execution):

```bash
# Add PREDICTION_HUNT_API_KEY to pmxt/.env first
./scripts/ph-sports-compare.sh slate nba
./scripts/ph-sports-compare.sh url https://kalshi.com/markets/kxwcgame/world-cup-game
```

### Agent skills and rules (project)

| Path | Purpose |
|------|---------|
| `.cursor/skills/pmxt-kalshi-trading/` | Fast live Kalshi playbook |
| `.cursor/skills/pmxt-cli/` | CLI, sidecar, `--local` vs `--hosted` |
| `.cursor/skills/prediction-hunt/` | PH sports odds comparison (pre-trade) |
| `.cursor/skills/scout-research/` | Scout research lane |
| `.cursor/skills/trader-execute/` | Trader execution lane |
| `.cursor/skills/multi-agent-handoff/` | Role switching, briefs, providers |
| `.cursor/rules/multi-agent-core.mdc` | Always-on multi-agent protocol |
| `.cursor/rules/scout-research.mdc` | Scout-only constraints |
| `.cursor/rules/trader-execute.mdc` | Trader-only constraints |
| `.cursor/rules/pmxt-trading.mdc` | PMXT safety reference |

**Agent execution rules:** use `event --event-id` (from Kalshi page footer), not
text search; max 2 preparatory CLI calls before presenting a trade; confirm with
the user before `order:create`; no MCP/Router for single-venue live trades.
Use PH scripts only **before** kickoff to pick venue/price — never during live execution.

### Multi-agent system (Scout / Trader)

Separate research from execution — see `docs/multi-agent.md` and `config/agents.json`.

```bash
./scripts/new-brief.sh my-market
./pmx scout grok                             # fast Scout (xAI)
./pmx scout claude                           # deep Scout (Anthropic)
./pmx trader openai briefs/active/DATE-my-market.md
./scripts/check-providers.sh                 # verify API keys
./scripts/install-hermes-skills.sh           # once, for Hermes
```

LLM keys live in `pmxt/.env` → synced by `./scripts/setup-hermes.sh`. See `docs/providers.md` and `config/providers.json`.

| Role | Cursor rule | Skills |
|------|-------------|--------|
| Scout | `scout-research` | scout-research, prediction-hunt, multi-agent-handoff |
| Trader | `trader-execute` | trader-execute, pmxt-kalshi-trading, multi-agent-handoff |

Other providers: `grok`, `claude`, `openai`, `codex`, `hermes`, `cursor` via `./scripts/agent-run.sh` or `./pmx scout|trader`.

Briefs require `approved: true` before Trader prepares orders.

### Hermes setup

One-time:

```bash
./scripts/setup-hermes.sh
```

This syncs `PMXT_API_KEY` and LLM keys (`XAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) from `pmxt/.env` to `~/.hermes/.env`, **disables pmxt MCP by default** (Grok/xAI schema errors), links project skills, and creates `/pmxtrader-scout` and `/pmxtrader-trader` bundles. See `hermes/README.md` and `docs/providers.md`.

To enable pmxt MCP for Claude/Codex only: `./scripts/setup-hermes.sh --with-mcp` (do not use with Grok).
