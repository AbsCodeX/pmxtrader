# Functionality review — 2026-06-19

**Linear parent:** [ABI-65](https://linear.app/pmxt/issue/ABI-65/functionality-review-2026-06-19)  
**Sub-issues:** ABI-66–ABI-71  
**Smoke script:** `scripts/smoke-functionality.sh`

Related: [ABI-58](https://linear.app/pmxt/issue/ABI-58) UI review, [ABI-43](https://linear.app/pmxt/issue/ABI-43) API integration

---

## Checklist (audit criteria)

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| App starts correctly | **Pass** | `./pmx help`; `./pmxt-cockpit.sh` creates venv + `python -m apps.cockpit`; dashboard health wait in `pmxt-dashboard.sh` |
| CLI/dashboard works | **Pass** | `resolve_dashboard_command` allows status/quote/markets/warm; blocks trades/agents; `tests/test_functionality.py` |
| Market search works | **Pass** | `./pmx poly markets [query]` → `fetch_poly_markets()` JSON/text parser; Markets pane + dashboard allowlist |
| Price/order book data loads | **Pass (when sidecar up)** | `./pmx quote`, `./pmx poly quote`, link analyzer via `/api/analyze`; requires warmed PMXT sidecar + keys |
| Balance/positions display correctly | **Pass** | `parse_status()` + cockpit `fetch_snapshot()` / `_positions_preview()`; home modules + status bar |
| Manual mode works | **Pass** | Palette allowlist, dashboard safe-run, Analyze/Markets panes, `./pmx` shortcuts |
| AI/bot mode stays controlled | **Pass** | Scout/trader blocked on web dashboard; cockpit AI confirm modal; `agent-run.sh` brief `approved: true` gate |

---

## Entry points

| Command | Role |
|---------|------|
| `./pmx help` | CLI router / aliases |
| `./pmx dashboard` | Web command center + `/api/health` |
| `./pmx cockpit` | Textual TUI (`.venv-cockpit`) |
| `./scripts/agent-run.sh scout\|trader` | Hermes/LLM agents (Trader needs approved brief) |

---

## Live vs offline testing

| Layer | Offline (CI) | Live (manual) |
|-------|--------------|---------------|
| Command routing | `tests/test_functionality.py` | `./pmx status` after `./pmx warm` |
| Market search parse | Mocked JSON in tests | `./pmx poly markets world` |
| Quote / book | Not in CI (needs sidecar) | `./pmx quote EVENT USA 1` |
| Balances | Parsed from fixture stdout | `./pmx balance`, `./pmx poly balance` |
| AI agents | Brief gate test only | `./pmx scout grok` with Hermes keys |

Run offline smoke: `./scripts/smoke-functionality.sh`

---

## Fixes applied (Batch H)

| Linear | Fix |
|--------|-----|
| [ABI-66](https://linear.app/pmxt/issue/ABI-66) | `tests/test_functionality.py` — 30 smoke tests across checklist |
| [ABI-70](https://linear.app/pmxt/issue/ABI-70) | `scripts/smoke-functionality.sh` + CI step |
| [ABI-67](https://linear.app/pmxt/issue/ABI-67) | Market/balance/positions parser tests in suite |
| [ABI-69](https://linear.app/pmxt/issue/ABI-69) | AI/bot control tests (dashboard block, brief gate) |
| [ABI-68](https://linear.app/pmxt/issue/ABI-68) | App startup smoke (pmx help, cockpit import, dashboard module) |
| [ABI-71](https://linear.app/pmxt/issue/ABI-71) | Review mirror (this file + `linear-task-func.md`) |

---

## Remaining gaps (accepted)

| Gap | Severity | Notes |
|-----|----------|-------|
| No CI live sidecar | Info | Venue APIs need keys + network; manual `./pmx warm` before trading |
| Hermes agent E2E not in CI | Low | Requires LLM keys; brief gate tested offline |
| Order book streaming not UI-tested | Low | `./pmx watch` is Terminal-only by design |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch H | 6 (ABI-66–ABI-71) | 6 |
| **Parent ABI-65** | **6 sub-issues** | **6** |
