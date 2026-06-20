# Project structure review — 2026-06-19

**Linear parent:** [ABI-79](https://linear.app/pmxt/issue/ABI-79/project-structure-review-2026-06-19)  
**Sub-issues:** ABI-80–ABI-85  
**Guide:** `docs/project-structure.md`

---

## Checklist (audit criteria)

| Criterion | Verdict | Notes |
|-----------|---------|-------|
| Folder organization | **Pass (after Batch J)** | Clear split: `apps/`, `dashboard/`, `scripts/`, `config/`, `pmxt/` vendor; placeholder READMEs added |
| Main entry points | **Pass** | `./pmx`, cockpit, dashboard server, agent-run, kill-switch — documented + tested |
| Config separation | **Pass** | Policy in `config/`; secrets in `pmxt/.env` only; tests assert no keys in agents.json |
| API/service separation | **Pass** | `apps/bridge` (shared) · `scripts/` (shell/API) · `pmxt/` (engine) · UI layers isolated |
| Wallet/trading logic isolation | **Pass** | No wallet code in pmxtrader; `trade_safety.py` + kill-switch in scripts; keys only in pmxt/.env |
| Naming clarity | **Pass (after Batch J)** | `apps/dashboard/` marked deprecated; root `dashboard/` is canonical; bridge layers documented |
| Unused or duplicate files | **Pass (after Batch J)** | Empty scaffolds documented; stale `architecture.md` fixed; tsconfig drops unused `packages/**` |

---

## Structure map

```
Entry          →  Orchestration           →  Engine
./pmx          →  scripts/*.sh            →  pmxt CLI → sidecar
cockpit        →  apps/cockpit/bridge     →  apps/bridge → subprocess
dashboard      →  pmxt-dashboard-server   →  apps/bridge → subprocess
agents         →  agent-run.sh            →  Hermes (external)
```

---

## Duplicates / dead scaffold

| Item | Status | Action |
|------|--------|--------|
| `apps/dashboard/` (empty) | Duplicate name | README: use root `dashboard/` |
| `apps/cli/` (empty) | Unused | README: use `./pmx` |
| `packages/*` (empty) | Unused | README + removed from tsconfig include |
| `tools/*` (empty) | Unused | README reserved |
| Root `dist/` | Gitignored tsc output | Documented in project-structure.md |
| Root npm devDeps | Scaffold | Documented in dependencies review |

---

## Fixes applied (Batch J)

| Linear | Fix |
|--------|-----|
| [ABI-80](https://linear.app/pmxt/issue/ABI-80) | Rewrote `docs/architecture.md` to match repo |
| [ABI-81](https://linear.app/pmxt/issue/ABI-81) | Added `docs/project-structure.md` |
| [ABI-82](https://linear.app/pmxt/issue/ABI-82) | Placeholder READMEs in empty dirs |
| [ABI-83](https://linear.app/pmxt/issue/ABI-83) | `tests/test_project_structure.py` invariants |
| [ABI-84](https://linear.app/pmxt/issue/ABI-84) | Trim `tsconfig.json` packages include |
| [ABI-85](https://linear.app/pmxt/issue/ABI-85) | Review mirror (this file + `linear-task-structure.md`) |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch J | 6 (ABI-80–ABI-85) | 6 |
| **Parent ABI-79** | **6 sub-issues** | **6** |
