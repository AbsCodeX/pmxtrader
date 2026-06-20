# UI / Dashboard review — 2026-06-19

**Linear parent:** [ABI-58](https://linear.app/pmxt/issue/ABI-58/ui-dashboard-review-2026-06-19)  
**Sub-issues:** ABI-59–ABI-64  
**Scope:** Web dashboard (`dashboard/`) + Cockpit TUI (`apps/cockpit/`)

Related: [ABI-5](https://linear.app/pmxt/issue/ABI-5) security/UX batch (complete), [ABI-51](https://linear.app/pmxt/issue/ABI-51) dependency review (complete)

---

## Checklist (audit criteria)

| Criterion | Verdict | Notes |
|-----------|---------|-------|
| Layout is clear | **Pass** | Web: card grid + tabs + analyzer + terminal. Cockpit: nav + modules + activity log |
| Manual mode and AI mode are separated | **Pass (after Batch G)** | Web: Manual/AI badges on cards; header clarifies AI in Cockpit. Cockpit: tab 2 = AI Chat, others manual |
| Trade preview is visible | **Pass (after Batch G)** | `extract_trade_preview()` highlights Price/Fill est lines in web preview box + cockpit analyze |
| Confirm button is clear | **Pass** | Web: no trade execution (by design); trade cmds labeled "Copy to Terminal". Cockpit: ConfirmCommandModal + visible "Run suggested" button |
| Errors are understandable | **Pass (after Batch G)** | Web: `friendlyApiError()` for 403/400/5xx. Cockpit: worker errors surfaced in chat/analyze |
| Logs/status are visible | **Pass** | Web: status bar + mini terminal + analyze output. Cockpit: ticker + ActivityLog + pane logs |
| Mobile/desktop layout works | **Pass (web)** | Responsive grid + stacked analyze row @820px; single column @640px. Cockpit TUI: desktop-first (N/A mobile) |

---

## Architecture (two UIs)

```
Web dashboard (dashboard/)
  Manual: safe-run commands, link analyzer preview, copy trade cmds → Terminal
  AI: copy-only Scout/Trader cmds (no execution from browser)

Cockpit TUI (apps/cockpit/)
  Manual: tabs 1,3–7 (home, analyze, positions, markets, diag, safety)
  AI: tab 2 (chat) — suggestions require ConfirmCommandModal or Ctrl+Enter
  Trades: Safety tab + confirm modals; palette blocks trade cmds
```

---

## Findings and fixes (Batch G)

| Linear | Issue | Fix applied |
|--------|-------|-------------|
| [ABI-63](https://linear.app/pmxt/issue/ABI-63) | No structured trade preview | `extract_trade_preview()` in `apps/bridge/parse.py`; web preview box + cockpit analyze header |
| [ABI-59](https://linear.app/pmxt/issue/ABI-59) | Manual/AI not visually separated on web | Split Research card; Manual/AI badges; header subtext |
| [ABI-61](https://linear.app/pmxt/issue/ABI-61) | Opaque API errors on web | `friendlyApiError()` + `postJson()` helper in `dashboard/js/app.js` |
| [ABI-62](https://linear.app/pmxt/issue/ABI-62) | AI confirm easy to miss | Cockpit "Run suggested command" button; worker error text in chat/analyze |
| [ABI-64](https://linear.app/pmxt/issue/ABI-64) | Trade copy unclear; mobile analyze buttons | "Copy to Terminal" for trade tag; responsive btn-row + single-column grid |
| [ABI-60](https://linear.app/pmxt/issue/ABI-60) | No review mirror | This file + `linear-task-ui.md` |

---

## Remaining gaps (accepted)

| Gap | Severity | Notes |
|-----|----------|-------|
| Web dashboard cannot confirm trades | Info | Intentional safety — Terminal/Cockpit only |
| Cockpit not mobile-optimized | Low | TUI assumes desktop terminal |
| Preview parsing is line-prefix heuristic | Low | Covers Kalshi eval + Poly link output; extend prefixes if formats change |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch G | 6 (ABI-59–ABI-64) | 6 |
| **Parent ABI-58** | **6 sub-issues** | **6** |
