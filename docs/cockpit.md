# pmxtrader cockpit (`pmx cockpit`)

Textual terminal dashboard for live balances, markets, diagnostics, AI chat, and safety controls.

## Launch

```bash
pmx cockpit          # or pmxt-cockpit / pmxt-terminal
```

Keys: **1** Dashboard · **2** Chat · **3** Analyze · **4** Positions · **5** Markets · **6** Diagnostics · **7** Safety · **/** palette · **r** refresh · **q** quit

## Architecture

| Layer | Path | Role |
|-------|------|------|
| App | `apps/cockpit/app.py` | Navigation, single 12s poll coordinator |
| Screens | `apps/cockpit/screens/` | Tab panes |
| Bridge | `apps/cockpit/bridge/` | `./pmx` subprocess, live data, AI |
| Shared | `apps/bridge/` | Status parsing + command policy (also used by web dashboard) |
| Widgets | `apps/cockpit/widgets/` | Ticker, stats bar, modals |

## Live refresh

One background worker in `app.py` calls `fetch_dashboard()` every **12 seconds**. Results update the ticker bar and home dashboard modules — no duplicate polling.

Manual refresh: **r** or the ↻ button on the dashboard tab.

Balance sparklines accumulate in `~/.pmxt-cockpit/balance-history.json`.

## Safety model

| Action | Where | Notes |
|--------|-------|-------|
| Read-only commands | Chat (auto), palette (allowlist) | status, balance, poly markets, etc. |
| Mutating commands | Chat confirm modal | stop, resume |
| Trades / panic | Safety tab only | PANIC requires typing `PANIC` in modal, then runs `./pmx panic --yes` |
| Unknown AI suggestions | Blocked | Use Terminal or Safety tab |

**Kill switch display:** `./pmx status` prints `ENGAGED` when halted. The UI maps that to **ON** (red).

## Web dashboard (`pmx dashboard`)

- Binds **127.0.0.1** only by default (set `PMXT_DASHBOARD_INSECURE_BIND=1` to bind elsewhere)
- Session token injected into served `index.html` only — **not** returned by `/api/health`
- Token also written to `.pmxt-dashboard.token` with mode **600**
- POST `/api/run` and `/api/analyze` require header `X-Pmxtrader-Token`
- Subprocesses get a **minimal env** (no full parent shell secrets)
- No CORS — same-origin only
- Trades blocked by deny-by-default allowlist

```bash
pmx dashboard              # foreground (blocks shell)
./scripts/pmxt-dashboard.sh start-bg   # background daemon
```

## Dependencies

```bash
pip install -r requirements-cockpit.txt
```

Creates `.venv-cockpit/` on first `pmxt-cockpit` run.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Kill switch shows `?` | Run `./pmx status` — should show ENGAGED or OFF |
| PANIC does nothing | Use Safety tab, type PANIC in modal (not old confirm-only flow) |
| Dashboard API 403 | Reload page from `http://127.0.0.1:8765/` (token injected at serve time, not via health) |
| Stale balances | `./pmx warm` or `./scripts/pmxt-server.sh restart` |

## Tests

```bash
python3 -m pytest tests/ -q
```
