# Testing

Last reviewed: **2026-06-19** (Batch K — see `reviews/2026-06-19/documentation-review.md`).

pmxtrader CI runs **offline** tests — no live venue API keys required.

---

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

**Editor setup:** open the repo in Cursor/VS Code and install recommended extensions (`.vscode/extensions.json`).

---

## Quick smoke (recommended after changes)

```bash
# Full Python suite (~78 tests)
python3 -m pip install -r requirements-cockpit.txt pytest ruff mypy pip-audit
python3 -m pytest tests/ -q

# Functionality smoke (pmx help, cockpit import, dashboard module)
./scripts/smoke-functionality.sh
```

CI runs pytest + `./scripts/smoke-functionality.sh --skip-pytest` (pytest already ran).

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
| `tests/test_trade_safety.py` | Kill switch guards, dry-run, max size |
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
