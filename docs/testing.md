---
description: pytest, CI, lint, docs quality checks, and PMXT engine tests.
---

<div class="pmx-page-hero" markdown="1">

# Testing & CI

<p class="pmx-page-lead">
pmxtrader CI runs offline — no live venue keys required. Docs, Python tests, lint, and type checks run on every push.
</p>

</div>

## Documentation quality (CI)

```bash
pip install -r requirements-docs.txt
npm install   # markdownlint-cli2 in devDependencies
npm run docs:lint
npm run docs:build
npm run docs:serve   # http://127.0.0.1:8000
```

| Check | Command |
|-------|---------|
| Markdown style | `npm run docs:lint` (markdownlint-cli2) |
| Broken links | `lychee --config .lychee.toml README.md docs/` |
| Site build | `npm run docs:build` (`mkdocs build --strict`) |

CI runs all three on every push. Published to **GitHub Pages** on `main` via `.github/workflows/docs-publish.yml`.

**Editor setup:** install recommended extensions from `.vscode/extensions.json`.

---

## Python venv (local = CI)

CI (`.github/workflows/ci.yml`) installs `ruff`, `mypy`, `pytest`, `pip-audit`, then
`requirements-cockpit.txt`, `requirements-docs.txt`, and `requirements-telegram.txt` before
`python -m pytest tests/ -q`.

One-time setup:

```bash
./scripts/setup-python-dev.sh
```

Or manually:

```bash
python3 -m venv .venv
.venv/bin/pip install -U pip ruff mypy pytest pip-audit
.venv/bin/pip install -r requirements-dev.txt
```

Run tests (use the project venv — system `python3` may lack pytest):

```bash
.venv/bin/python -m pytest tests/ -q
```

---

## Quick smoke (recommended after changes)

```bash
./scripts/setup-python-dev.sh   # if .venv not ready
.venv/bin/python -m pytest tests/ -q
./scripts/smoke-functionality.sh
```

CI runs pytest + `./scripts/smoke-functionality.sh --skip-pytest` (pytest already ran).

### Preflight exit codes

`./pmx preflight` (and `./pmx check`) use distinct exit codes for automation:

| Code | Meaning |
|------|---------|
| `0` | **GO** — live trading allowed (sidecar OK, keys present, kill switch off, read-only off) |
| `1` | **NO-GO (safe)** — expected safety blocks (read-only, kill switch, daily loss cap) |
| `2` | **BROKEN** — fix infra first (sidecar down, no venue keys, invalid size cap) |

Example: `./pmx preflight; echo $?`

---

## Lint and type check

```bash
python3 -m ruff check .
python3 -m mypy . --ignore-missing-imports
python3 scripts/pre_commit_secret_check.py
```

---

## Dependency audits

```bash
npm audit --audit-level=high          # root scaffold
pip-audit -r requirements-cockpit.txt
```

See `docs/dependencies.md` for inventory and vendor policy.

---

## Test layout

| Path | Covers |
|------|--------|
| `tests/test_functionality.py` | CLI routing, dashboard allowlist, parsers |
| `tests/test_trade_safety.py` | Kill switch guards, dry-run, max size, preflight exit codes, panic dry-run |
| `tests/test_project_structure.py` | Entry points, config separation |
| `tests/test_documentation.py` | Doc links and referenced scripts exist |
| `tests/test_dashboard_security.py` | Loopback bind, minimal env |
| Other `tests/test_*.py` | Bridge parse, cockpit, API integration |

---

## PMXT engine tests (vendored `pmxt/`)

These are **upstream** tests — run when changing PMXT or debugging sidecar issues:

```bash
npm run build --workspace=pmxt-core --prefix pmxt
npm test --workspace=pmxt-core --prefix pmxt    # ~650 Jest unit tests
cd pmxt && npm test                             # full verify-all (needs network)
```

See `AGENTS.md` and `pmxt/CONTRIBUTING.md`.

---

## Manual live checks (needs keys + network)

Not run in CI. After `./pmx warm`:

```bash
./pmx status
./pmx balance
./pmx poly balance
./pmx quote EVENT OUTCOME 1 --dry-run    # if applicable
```

Trading safety dry-run: `./pmx trade MARKET OUT 1 --dry-run` (no order placed).
