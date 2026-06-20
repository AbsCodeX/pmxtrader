---
description: Python, npm, and vendored PMXT dependency inventory.
---

<div class="pmx-page-hero pmx-glass" markdown="1">

# Dependencies

<p class="pmx-page-lead">
Pinned manifests for pmxtrader-owned code. The vendored <code>pmxt/</code> subtree maintains its own lockfile and audit policy.
</p>

<div class="pmx-pill-row">
  <span class="pmx-pill">Reviewed 2026-06-19</span>
</div>

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

**DevDependencies** (scaffold only — see `AGENTS.md`):

| Package | Version | Used in CI? |
|---------|---------|-------------|
| typescript | ^5.4.5 | No |
| ts-node | ^10.9.2 | No |
| eslint | ^8.57.0 | No |
| @typescript-eslint/* | ^7.13.0 | No |
| @types/node | ^20.14.0 | No |

**Audit:** `npm audit` at repo root → **0 vulnerabilities** (2026-06-19).

---

## npm — vendored PMXT (`pmxt/` submodule)

Managed upstream at [pmxt-dev/pmxt](https://github.com/pmxt-dev/pmxt). Key manifests:

| Workspace | Version | Notable runtime deps |
|-----------|---------|----------------------|
| pmxt-core | 2.17.1 | axios ^1.17.0, express ^5.2.1, ethers ^5.8.0, viem ^2.0.0, ws ^8.18.0, polymarket-us 0.1.1 |
| @pmxt/cli | 2.17.1 | @oclif/core ^4.11.4, ws ^8.18.0 |
| pmxtjs (typescript SDK) | 2.17.1 | axios, ws (via generated client) |
| pmxt-monorepo root | — | pmxtjs ^2.17.1, viem 2.48.4 (override), cli-progress ^3.12.0 |

**Audit:** `cd pmxt && npm audit` → **66 vulnerabilities** (4 critical, 10 high, 39 moderate, 13 low) as of 2026-06-19.

**Remediation policy:** Do **not** run `npm audit fix --force` in this repo. Track upstream PMXT releases and bump the submodule intentionally. Runtime-critical items to watch:

- **axios** (pmxt-core direct) — multiple high SSRF/header issues; needs upstream bump to ≥1.16+
- **ws** (@pmxt/cli direct) — high severity; bump when upstream allows
- **ethers v5 / elliptic** — moderate; major ethers v6 migration is breaking
- **Dev-only:** `@openapitools/openapi-generator-cli` pulls critical **basic-ftp**, **shell-quote**, **concurrently** — only used at SDK generation time, not in the sidecar runtime bundle

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
