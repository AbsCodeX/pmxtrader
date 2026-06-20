---
description: Textual cockpit TUI — balances, markets, diagnostics, and safety controls.
---

<div class="pmx-page-hero" markdown="1">

# Cockpit TUI

<p class="pmx-page-lead">
Terminal dashboard for live balances, market data, diagnostics, and safety actions.
Mutating commands require explicit confirmation; trades and panic run only from the Safety tab.
</p>

</div>

## Launch

```bash
./pmx cockpit          # alias: pmxt-cockpit
```

| Key | Pane |
|-----|------|
| **1** | Dashboard |
| **2** | Chat |
| **3** | Analyze |
| **4** | Positions |
| **5** | Markets |
| **6** | Diagnostics |
| **7** | Safety |
| **/** | Command palette |
| **r** | Refresh live data |
| **q** | Quit |

---

## Architecture

| Layer | Path | Role |
|-------|------|------|
| App | `apps/cockpit/app.py` | Navigation, single poll coordinator |
| Screens | `apps/cockpit/screens/` | Tab panes |
| Bridge | `apps/cockpit/bridge/` | `./pmx` subprocess, live data, AI |
| Shared | `apps/bridge/` | Status parsing + command policy (web dashboard) |
| Widgets | `apps/cockpit/widgets/` | Ticker, stats bar, modals |

---

## Live refresh

One background worker in `app.py` calls `fetch_dashboard()` every **12 seconds**. Results update the ticker bar and home modules — no duplicate polling.

Manual refresh: **r** or the refresh control on the dashboard tab.

Balance history accumulates in `~/.pmxt-cockpit/balance-history.json`.

---

## Safety model

| Action | Where | Notes |
|--------|-------|-------|
| Read-only commands | Chat (auto), palette (allowlist) | status, balance, poly markets, etc. |
| Mutating commands | Chat confirm modal | stop, resume |
| Trades / panic | Safety tab only | PANIC requires typing `PANIC`, then `./pmx panic --yes` |
| Unknown AI suggestions | Blocked | Use Terminal or Safety tab |

**Kill switch display:** `./pmx status` prints `ENGAGED` when halted. The UI maps that to **ON** (red).

!!! warning "Cockpit is not the web dashboard"
    `./pmx dashboard` is a separate browser UI. Both block web-side trade execution; Cockpit can run guarded live actions via the Safety tab.

---

## Web dashboard (`./pmx dashboard`)

| Property | Behavior |
|----------|----------|
| Bind address | `127.0.0.1` default (`PMXT_DASHBOARD_INSECURE_BIND=1` to widen) |
| Session token | Injected into served HTML only — not returned by `/api/health` |
| Token file | `.pmxt-dashboard.token` mode **600** |
| API auth | Header `X-Pmxtrader-Token` on POST `/api/run`, `/api/analyze` |
| Subprocess env | Minimal env — no full parent shell secrets |
| CORS | Same-origin only |
| Trades | Blocked by deny-by-default allowlist |

```bash
./pmx dashboard                        # foreground
./scripts/pmxt-dashboard.sh start-bg   # background daemon
```

See [Known risks](known-risks.md#execution-surfaces) for the execution surface matrix.

---

## Dependencies

```bash
pip install -r requirements-cockpit.txt
```

First `./pmx cockpit` run creates `.venv-cockpit/` if needed.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Kill switch shows `?` | Run `./pmx status` — should show ENGAGED or OFF |
| PANIC does nothing | Safety tab → type PANIC in modal |
| Dashboard API 403 | Reload from `http://127.0.0.1:8765/` (token injected at serve time) |
| Stale balances | `./pmx warm` or `./scripts/pmxt-server.sh restart` |

---

## Tests

```bash
python3 -m pytest tests/ -q
```

Related: [Environment & safety](environment.md#dashboard-cockpit) · [Command reference](commands.md#start-a-session)
