# Code review — cockpit, scripts, web dashboard

**Date:** 2026-06-19  
**Scope:** `apps/cockpit/`, `scripts/`, `dashboard/` + `scripts/pmxt-dashboard-server.py`  
**Linear parent:** [ABI-5](https://linear.app/pmxt/issue/ABI-5/code-review-cockpit-scripts-web-dashboard-2026-06-19) — **Done** (37 sub-issues ABI-6–ABI-42)

---

## Reference (summary)

Reviewed 27 Python files in `apps/cockpit/`, 40 files in `scripts/`, and the web dashboard stack (`dashboard/`, `pmxt-dashboard-server.py`, `pmxt-dashboard.sh`).

**Strengths:** Subprocess calls use argv lists (no `shell=True`); trading goes through deny-by-default allowlists in `apps/bridge/commands.py`; kill switch checked before live orders; `check-providers.sh` never prints secrets.

**Top risks (all addressed):** Dashboard token exposure; hardcoded `pmxt` paths; cockpit AI auto-run; Rich markup injection; monolithic `index.html` (split into `dashboard/css/` + `dashboard/js/`).

---

## Ordered findings (fix queue)

Format: `file → problem → suggested fix → done?`

### Critical — wrong behavior / safety / money at risk

1. `scripts/pmxt-dashboard-server.py` → `/api/health` returns token → remove token from health; inject at serve time → [x]
2. `scripts/polymarket-us-quickstart.sh` → hardcoded `pmxt` → `pmxt_cli` → [x]
3. `scripts/kalshi-emergency-exit.py` → hardcoded `pmxt` → `pmxt_cli` → [x]
4. `apps/cockpit/screens/chat.py` → AI auto-runs safe commands → confirm all suggestions → [x]

### High — reliability, security, big UX breaks

5. Token file mode 600 → [x]
6. Minimal subprocess env → [x]
7. Loopback bind guard → [x]
8. PID flock + health poll → [x]
9. Rich markup escape → [x]
10. Diagnostics `table.clear(columns=False)` → [x]
11. Worker ERROR handling → [x]
12. Analyze size validation → [x]
13. Palette dashboard confirm → [x]
14. Generic OS toasts → [x]
15. Token not from health endpoint → [x]

### Medium / Low — cleanup, docs, dead code

16–37. See Linear ABI-20–ABI-42 → [x]

---

## Progress

| Severity | Total | Done |
|----------|-------|------|
| Critical | 4 | 4 |
| High | 11 | 11 |
| Medium/Low | 22 | 22 |
| **All** | **37** | **37** |

**Follow-up (post-audit):** Split web dashboard into `dashboard/index.html`, `dashboard/css/app.css`, `dashboard/js/app.js`; root `index.html` redirects for offline bookmarks.
