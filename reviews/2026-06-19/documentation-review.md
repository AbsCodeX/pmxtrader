# Documentation review — 2026-06-19

**Linear parent:** [ABI-79](https://linear.app/pmxt/issue/ABI-79/documentation-review-2026-06-19)  
**Sub-issues:** ABI-80–ABI-85  

---

## Checklist (audit criteria)

| Criterion | Verdict | Notes |
|-----------|---------|-------|
| README accuracy | **Pass (after Batch K)** | Structure table fixed; safety env vars; doc index; submodule init |
| Setup instructions | **Pass** | direnv, setup-dev, setup-hermes, credentials table → setup guides |
| Run commands | **Pass** | Quick start + daily trading + multi-agent — matches `scripts/pmx.sh` |
| Test commands | **Pass (after Batch K)** | New `docs/testing.md`; README Testing section; CI documented |
| Environment variable explanations | **Pass (after Batch K)** | New `docs/environment.md`; README links; `pmxt/.env.example` |
| Official links | **Pass (after Batch K)** | New `docs/official-links.md` (PMXT, venues, LLM dashboards) |
| Known risks / limitations | **Pass (after Batch K)** | New `docs/known-risks.md` (real money, agents, sidecar, CI gaps) |

---

## Gaps found (before Batch K)

| Gap | Severity | Fix |
|-----|----------|-----|
| No test commands in README | Medium | `docs/testing.md` + README section |
| Safety env vars undocumented in user docs | Medium | `docs/environment.md` + README Safety |
| Stale project structure table | Low | README + link to `docs/project-structure.md` |
| No centralized official links | Low | `docs/official-links.md` |
| Risks scattered across AGENTS.md / safety review | Low | `docs/known-risks.md` |
| `architecture.md` missing doc review link | Low | Audit trail updated |

---

## Fixes applied (Batch K)

| Linear | Fix |
|--------|-----|
| [ABI-80](https://linear.app/pmxt/issue/ABI-80) | `docs/environment.md` |
| [ABI-81](https://linear.app/pmxt/issue/ABI-81) | `docs/testing.md` |
| [ABI-83](https://linear.app/pmxt/issue/ABI-83) | `docs/known-risks.md`, `docs/official-links.md` |
| [ABI-85](https://linear.app/pmxt/issue/ABI-85) | README updates |
| [ABI-84](https://linear.app/pmxt/issue/ABI-84) | `tests/test_documentation.py` (9 tests) |
| [ABI-82](https://linear.app/pmxt/issue/ABI-82) | Review mirror (this file + `linear-task-docs.md`) |

---

## Doc map

| Audience | Start here |
|----------|------------|
| New operator | README → `setup-dev.sh` → `pmxt/.env` → `./pmx warm` |
| Daily trading | `docs/commands.md` |
| Env / safety | `docs/environment.md`, `docs/known-risks.md` |
| Developers | `docs/testing.md`, `AGENTS.md` |
| Layout | `docs/project-structure.md` |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch K | 6 (ABI-80–ABI-85) | 6 |
| **Parent ABI-79** | **6 sub-issues** | **6** |
