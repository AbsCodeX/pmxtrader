# Dependency review — 2026-06-19

**Linear parent:** [ABI-51](https://linear.app/pmxt/issue/ABI-51/dependency-review-2026-06-19)  
**Sub-issues:** ABI-52–ABI-57  
**Inventory doc:** `docs/dependencies.md`

---

## Checklist (audit criteria)

| Criterion | Verdict | Notes |
|-----------|---------|-------|
| package.json / requirements reviewed | **Pass** | Root npm, cockpit Python, pmxt submodule manifests mapped in `docs/dependencies.md` |
| Suspicious packages flagged | **Pass** | No typosquats; niche exchange SDKs noted; dev-only critical chain documented |
| Install scripts reviewed | **Pass** | No `postinstall`/`preinstall`; `prepack` is local validate only; setup scripts reviewed |
| Audit command run | **Pass** | Root `npm audit` 0 vulns; `pip-audit` 0 vulns; pmxt `npm audit` 66 vulns (vendor, tracked) |
| Unused dependencies flagged | **Pass** | Root eslint/ts-node/typescript unused (documented in AGENTS.md); `@types/cli-progress` misplaced in pmxt root deps |
| Versions documented | **Pass** | `docs/dependencies.md` + tested cockpit pins in `requirements-cockpit.txt` header |

---

## Manifest summary

```
pmxtrader/
├── package.json              devDeps only (scaffold); 0 runtime deps; 0 audit vulns
├── requirements-cockpit.txt  textual, rich — 0 pip-audit vulns
├── .github/workflows/ci.yml  + npm audit + pip-audit (Batch F)
└── pmxt/                     vendored submodule — separate audit policy
    ├── core/package.json     pmxt-core runtime (axios, express, ethers, …)
    ├── sdks/cli/package.json @pmxt/cli (ws direct)
    └── sdks/python/pyproject.toml
```

---

## Audit results (2026-06-19)

### pmxtrader-owned — **clean**

| Command | Result |
|---------|--------|
| `npm audit` (root) | **0** vulnerabilities |
| `pip-audit -r requirements-cockpit.txt` | **0** known vulnerabilities |
| Installed cockpit versions | textual **8.2.7**, rich **15.0.0** |

### pmxt vendor — **66 vulnerabilities** (informational)

| Severity | Count |
|----------|-------|
| Critical | 4 |
| High | 10 |
| Moderate | 39 |
| Low | 13 |

**Notable packages:**

| Package | Severity | Direct in pmxt-core/cli? | Notes |
|---------|----------|--------------------------|-------|
| axios | High | Yes (core) | Sidecar HTTP client; fix requires upstream bump |
| ws | High | Yes (@pmxt/cli) | WebSocket client for watch/feed |
| elliptic / ethers v5 | Moderate | Transitive | Breaking fix → ethers v6 |
| @openapitools/openapi-generator-cli | Critical (transitive) | Dev only | basic-ftp, shell-quote — SDK codegen, not runtime |
| viem | Moderate | Yes | Pinned 2.48.4 at monorepo root via overrides |

**Policy:** Submodule bumps via intentional upstream sync — no blind `npm audit fix --force` in pmxtrader.

---

## Suspicious / unusual packages

| Package | Location | Verdict |
|---------|----------|---------|
| @buidlrrr/rain-sdk | pmxt-core | Legitimate Rain exchange SDK (verify publisher on bump) |
| @prob/clob, @prob/core | pmxt-core | Probable exchange CLOB — pinned 0.5.0 |
| @opinion-labs/opinion-clob-sdk | pmxt-core | Opinion Labs official SDK |
| polymarket-us | pmxt-core | Polymarket US venue client |
| basic-ftp | transitive (openapi-generator) | Dev toolchain only — not shipped in sidecar bundle |

No packages with install-time network fetch or obfuscated names found.

---

## Unused / misplaced dependencies

| Item | Issue | Action |
|------|-------|--------|
| Root `typescript`, `eslint`, `ts-node` | Placeholder devDeps; not in CI | Documented in AGENTS.md + `docs/dependencies.md` — remove when root TS lint is implemented |
| Root `"main": "dist/index.js"` | No root TS entrypoint built | Informational — scaffold artifact |
| pmxt root `@types/cli-progress` in `dependencies` | Should be devDependency | Flag for upstream PMXT PR |
| pmxt root `pmxtjs` + workspace SDK | Redundant but used by examples/tools | Keep; vendor concern |

---

## Install script review

| Script | Network / install behavior | Verdict |
|--------|---------------------------|---------|
| `scripts/setup-dev.sh` | `npm install -g @pmxt/cli`; submodule init; `npm run build --workspace=pmxt-core` | OK — trusted registry, no pipe-to-shell |
| `scripts/setup-hermes.sh` | Reads local auth JSON; syncs env files | OK |
| `pmxt/scripts/verify-all.sh` | `npm run build` in submodule | OK |
| `prepack` (@pmxt/cli, pmxtjs) | Local validation/build only | OK |
| **No** `postinstall` / `preinstall` in any reviewed `package.json` | — | **Pass** |

---

## Fixes applied (Batch F)

| Linear | Fix |
|--------|-----|
| [ABI-57](https://linear.app/pmxt/issue/ABI-57) | CI: `npm audit --audit-level=high` + `pip-audit` on cockpit requirements |
| [ABI-52](https://linear.app/pmxt/issue/ABI-52) | `docs/dependencies.md` version inventory |
| [ABI-53](https://linear.app/pmxt/issue/ABI-53) | pmxt vendor audit policy + counts in docs/review |
| [ABI-54](https://linear.app/pmxt/issue/ABI-54) | Unused/misplaced deps flagged (this doc + dependencies.md) |
| [ABI-55](https://linear.app/pmxt/issue/ABI-55) | Tested cockpit versions in requirements header |
| [ABI-56](https://linear.app/pmxt/issue/ABI-56) | Review mirror (`reviews/2026-06-19/*.md`) |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch F | 6 (ABI-52–ABI-57) | 6 |
| **Parent ABI-51** | **6 sub-issues** | **6** |
