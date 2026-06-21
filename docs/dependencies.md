---
description: Python, npm, and vendored PMXT dependency inventory.
---

<div class="pmx-page-hero" markdown="1">

# Dependencies

<p class="pmx-page-lead">
Pinned manifests for pmxtrader-owned code. The vendored <code>pmxt/</code> subtree maintains its own lockfile and audit policy.
</p>

</div>

## Python — cockpit (`requirements-cockpit.txt`)

| Package | Constraint | Tested (2026-06-19) | Role |
|---------|------------|---------------------|------|
| textual | `>=0.80.0` | 8.2.7 | Cockpit TUI |
| rich | `>=13.0.0` | 15.0.0 | Rich markup in cockpit widgets |

**Audit:** `pip-audit -r requirements-cockpit.txt` → **0 known vulnerabilities** (2026-06-19).

**CI dev tools** (installed in `.github/workflows/ci.yml`, not in requirements file):

| Tool | Purpose |
|------|---------|
| pytest | `tests/` |
| ruff | lint |
| mypy | type check |
| pip-audit | dependency audit gate |

---

## npm — root (`package.json`)

| Package | Version | Runtime | Notes |
|---------|---------|---------|-------|
| *(none)* | — | — | Root has **no runtime** npm dependencies |

**DevDependencies** (docs lint only):

| Package | Version | Used in CI? |
|---------|---------|-------------|
| markdownlint-cli2 | ^0.17.0 | Yes (`npx markdownlint-cli2`) |

Root `package.json` **does not** run TypeScript or ESLint — use `pmxt-core` build below.

**Audit:** `npm audit` at repo root → **0 vulnerabilities** (2026-06-21).

---

## npm — vendored PMXT (`pmxt/`)

Managed upstream at [pmxt-dev/pmxt](https://github.com/pmxt-dev/pmxt). Submodule conversion tracked in [`pmxt-submodule-migration.md`](pmxt-submodule-migration.md). Key manifests:

| Workspace | Version | Notable runtime deps |
|-----------|---------|----------------------|
| pmxt-core | 2.17.1 | axios ^1.17.0, express ^5.2.1, ethers ^5.8.0, viem ^2.0.0, ws ^8.21.0, polymarket-us 0.1.1 |
| @pmxt/cli | 2.17.1 | @oclif/core ^4.11.4, ws ^8.21.0 |
| pmxtjs (typescript SDK) | 2.17.1 | axios, ws (via generated client) |
| pmxt-monorepo root | — | pmxtjs ^2.17.1, viem 2.48.4 (override), cli-progress ^3.12.0 |

**Audit:** `cd pmxt && npm audit` → **51 vulnerabilities** (3 critical, 4 high, 32 moderate, 12 low) as of 2026-06-21 after `npm audit fix` + ws ^8.21.0 bump.

**Remediation policy:** Do **not** run `npm audit fix --force` in this repo (breaks ethers v5 → v6). Track upstream PMXT releases and bump the submodule intentionally. Accepted in pmxtrader until submodule sync:

- **ws** — bumped to ^8.21.0 in pmxt-core and @pmxt/cli; transitive copies in SDK deps remain
- **axios** (pmxt-core direct) — ^1.17.0; safe minor bumps applied via lockfile refresh
- **ethers v5 / elliptic / viem** — moderate; major ethers v6 migration is breaking
- **Dev-only:** `@openapitools/openapi-generator-cli` pulls critical **basic-ftp**, **shell-quote** — SDK generation only, not sidecar runtime bundle

---

## Python — PMXT SDK (`pmxt/sdks/python/pyproject.toml`)

Vendor subtree; not installed by pmxtrader CI. Documented for completeness:

| Package | Constraint |
|---------|------------|
| urllib3 | >=2.7.0 |
| python-dateutil | >=2.8.0 |
| pydantic | >=2.0.0 |
| typing-extensions | >=4.0.0 |

Version: **pmxt 2.18.0** (pyproject) vs **pmxt-core 2.17.1** (npm) — minor drift normal until submodule sync.

---

## Install scripts (lifecycle hooks)

| Location | Hook | Behavior | Risk |
|----------|------|----------|------|
| `@pmxt/cli` | `prepack` | Runs `validate.js` (local checks) | Low — no network |
| `pmxtjs` SDK | `prepack` | Runs local `build` | Low |
| All pmxtrader + pmxt `package.json` | `postinstall` / `preinstall` | **None found** | — |

Setup scripts (`scripts/setup-dev.sh`, `setup-hermes.sh`) use `npm install -g @pmxt/cli` from npm registry and `git submodule update` — no `curl | bash` patterns.

---

## Audit commands (local)

```bash
# pmxtrader-owned (must pass in CI)
npm audit --audit-level=high
pip install pip-audit && pip-audit -r requirements-cockpit.txt

# vendored PMXT (informational; not gated in pmxtrader CI)
cd pmxt && npm audit
```
