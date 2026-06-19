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
