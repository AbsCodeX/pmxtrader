# Live Readiness Report

Date: 2026-06-19  
Reviewer/Agent: Cursor Auto

## Feature Checklist

| Feature | Result | Notes |
|---------|--------|-------|
| Setup | Pass | `source scripts/pmxt-env.sh` loads `PMXTRADER_ROOT`, global `@pmxt/cli/2.50.2`; Kalshi + Polymarket US keys detected in `pmxt/.env` (values not logged). |
| App Startup | Pass | Preflight/status: sidecar healthy at `http://127.0.0.1:3848/health`. |
| CLI | Pass | `./pmx help`, `./pmx preflight`, `./pmx status`, `./pmx panic status` ran; `./pmx trade TEST OUT 1` blocked with read-only message (exit 1, no order). |
| Dashboard | Pass | `./scripts/smoke-functionality.sh --skip-pytest` imports dashboard server; `apps/bridge/commands.py` deny-lists `trade`/`poly trade`/panic/stop/resume; `pmxt-dashboard-server.py` returns 400 if command not on safe allowlist. Token required on API (`X-Pmxtrader-Token`). |
| Market Data | Pass | `./pmx status` returned Kalshi and Polymarket US balances via read-only API paths; no trading invoked. |
| Trading Dry-Run | Pass | `./pmx preview trade TEST OUT 1` and `./pmx preview poly trade test-slug long 1` printed `[dry-run]` only; `./pmx stop dry` (with network) previewed kill switch, cancels, and flatten as `dry_run` on both venues. |
| AI/Bot Mode | Needs Review | `./scripts/agent-run.sh` blocks Trader when brief frontmatter lacks `approved: true`; Scout has no execution gate. Agents still rely on human `./pmx go-live` + terminal `YES` for live `pmxt` orders — policy in `.cursor/rules`, not enforced in sidecar. |
| Logging | Pass | `apps/bridge/trade_audit.py` appends JSON lines to `briefs/alerts/trades.jsonl` (no secrets); preflight/trade scripts surface structured errors to stderr. |
| Error Handling | Needs Review | Read-only and kill-switch paths fail closed with clear messages. `./pmx stop dry` exited 0 with full network; in sandboxed network Kalshi position fetch failed (`Tunnel connection failed: 403`) after Poly US dry-run steps — panic preview should tolerate partial venue failures without scary tracebacks. |
| Tests/Build | Pass | `.venv-cockpit/bin/python -m pytest tests/ -q`: **114 passed**; `npm run build --workspace=pmxt-core --prefix pmxt` succeeded. System `python3 -m pytest` has no pytest module — use project venv. |

## Safety Findings

- Live trading accidentally triggered: **No**
- Real wallet required: **Yes** (live orders and panic flatten use funded venue accounts after `./pmx go-live`)
- Real API key required: **Yes** (Kalshi / Polymarket US keys in `pmxt/.env` for trading and authenticated reads)
- Secrets exposed in logs: **No** (verification output showed balances and order IDs only; no key material)
- Dry-run mode exists: **Yes** (`./pmx preview …`, `PMX_DRY_RUN` / `DRY_RUN` in `trade-safety-lib.sh`, `./pmx stop dry`, `./pmx panic --dry-run`)
- Kill switch works: **Yes** (file sentinel `KILL_SWITCH`; status OFF at test time; `./pmx stop`/`halt` documented; `trade_safety_require_live` checks switch)
- Manual approval required: **Yes** (default `PMX_READ_ONLY=1` until `./pmx go-live`; live trades require `trade_safety_confirm_live` / `YES` unless `--yes`; panic cash-out requires `PANIC`; Trader agent requires `approved: true` in brief)

---

## Must Fix Before Live Use

- None identified that bypass safeguards without operator action (`./pmx go-live`, kill switch off, explicit confirmation). Treat `./pmx preflight` exit **1** with only **Read-only mode FAIL** as expected safe posture, not infra failure.
- Before first live session in a new environment: run `./pmx preflight` only **after** intentional `./pmx go-live`, and confirm `./pmx stop dry` completes on your network (Kalshi + Poly US).

---

## Recommended Improvements

- Harden `./pmx stop dry` / `kalshi-emergency-exit.py` so a single venue network error does not emit a full Python traceback mid dry-run (continue with other venues, exit 0 when preview-only).
- Document canonical test command as `.venv-cockpit/bin/python -m pytest tests/ -q` (or `.venv/bin/pytest`) in CI/docs — matches `DRY_RUN_TEST_REPORT.md`.
- Optional: preflight wrapper or exit-code convention distinguishing “safe NO-GO (read-only)” vs “broken sidecar/keys.”
- Cockpit palette is deny-by-default for trades; keep dashboard token file mode `600` and rotate on shared machines.
- Re-run periodic `./pmx panic --dry-run` to validate flatten scope against current holdings (see also `DRY_RUN_TEST_REPORT.md`).

---

## Final Decision

**Final Decision:** Needs Review

**Reason:** Layered safeguards verified in this session: read-only default blocks `./pmx trade` without `./pmx go-live`; kill switch file + `apps/bridge/trade_safety.py` gates live paths; max size cap (10 contracts); sidecar preflight; dashboard/API deny-list for mutating commands; Trader brief `approved: true` gate in `agent-run.sh`. No live orders were placed. Terminal live trading after explicit `./pmx go-live` remains intentional and is acceptable **only with operator discipline** (preflight GO, per-order YES, kill switch awareness). **Needs Review** rather than unconditional **Go** because agent/LLM lanes are not cryptographically prevented from calling `pmxt` if the human has enabled live mode, and panic dry-run UX still needs resilience when one venue API fails. Cross-check: earlier same-day `DRY_RUN_TEST_REPORT.md` (Pass, low risk) aligns on read-only posture, preview/stop dry labeling, and venv pytest requirement.

**Final Instruction applied:** No path was found that places trades, moves funds, or bypasses approval **without** disabling read-only, clearing kill switch (where applicable), and human confirmation — so **No-Go** for unsafe automation is not warranted. Current session default remains **NO-GO for live** until operator runs `./pmx go-live` and preflight reports GO.
