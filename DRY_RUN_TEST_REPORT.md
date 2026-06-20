# Dry-Run Test Report

## Overall Result

Status: Pass  
Risk Level: Low  
Date: 2026-06-19  
Reviewer/Agent: Cursor agent / Auto  

---

## Commands Run

```bash
source scripts/pmxt-env.sh
cd /Users/astafford/pmxtrader

./pmx help
./pmx preflight
./pmx check
./pmx status
./pmx panic status
./pmx stop dry
./pmx panic --dry-run
./pmx preview trade DUMMY-MARKET OUT 1
./pmx preview poly trade dummy-slug long 1
.venv/bin/pytest tests/test_trade_safety.py -q
./scripts/smoke-functionality.sh --skip-pytest
```

---

## Results

| Command | Exit | Summary |
|---------|------|---------|
| `./pmx help` | 0 | Cheat sheet printed; documents `preview`, `preflight`, `panic --dry-run`, `stop dry`. |
| `./pmx preflight` | 1 | Sidecar OK (`127.0.0.1:3848`); kill switch OFF; read-only ON; max trade 10; Kalshi + Poly US keys present; **Live trading: NO-GO** (expected safe posture). |
| `./pmx check` | 1 | Same output as preflight (alias). |
| `./pmx status` | 0 | Kill switch OFF; read-only ON; panic scope includes Kalshi + Poly US; venue balances returned (read-only API). |
| `./pmx panic status` | 0 | Panic scope: Kalshi and Polymarket US both included. |
| `./pmx stop dry` | 0 | `[dry-run]` kill switch, cancel orders, flatten positions; all actions labeled `dry_run` (no execution). |
| `./pmx panic --dry-run` | 0 | Identical dry-run panic preview; enumerated resting orders and open positions with `-> dry_run`. |
| `./pmx preview trade DUMMY-MARKET OUT 1` | 0 | `[dry-run] Kalshi: would buy 1 on DUMMY-MARKET (OUT) @ market` — no order placed. |
| `./pmx preview poly trade dummy-slug long 1` | 0 | `[dry-run] Polymarket US: would buy 1 on dummy-slug (long) @ market` — no order placed. |
| `.venv/bin/pytest tests/test_trade_safety.py -q` | 0 | **35 passed** in ~0.04s. |
| `./scripts/smoke-functionality.sh --skip-pytest` | 0 | `pmx help` + dashboard import smoke passed. |

**Note:** `python3 -m pytest` without the project `.venv` fails (`No module named pytest`). Use `.venv/bin/pytest` or activate the venv first.

---

## Failures / Issues

1. **Preflight exit code 1** — Not a dry-run regression. Read-only mode is ON (`PMX_READ_ONLY` / no `.pmx-live`), which correctly blocks live trading. All other preflight checks passed.
2. **System Python pytest** — `python3 -m pytest tests/test_trade_safety.py -q` failed; tests pass when run via `/Users/astafford/pmxtrader/.venv/bin/pytest`.
3. **Env sourcing noise** — Sourcing `scripts/pmxt-env.sh` in non-interactive shells prints helper function definitions and a reminder to `source` the file; harmless but clutters captured output.

No live orders were submitted during this session.

---

## Safety Observations

- **Read-only gate active** — Preflight and status both report read-only ON; aligns with dry-run / no-live-trade intent.
- **Dry-run labeling consistent** — `preview trade`, `preview poly trade`, `stop dry`, and `panic --dry-run` all prefix or suffix actions with `[dry-run]` / `dry_run`; panic preview lists real positions/orders but does not mutate them.
- **Kill switch** — OFF at test time (new trades would still be blocked by read-only until `./pmx go-live`).
- **Credentials present** — Kalshi and Polymarket US keys detected in `pmxt/.env`; dry-run commands did not use them for order creation. Real balances and position inventories were read for panic preview only.
- **Trade safety tests** — 35 unit tests in `tests/test_trade_safety.py` passed under venv.

---

## Recommendations

1. Document or script default test invocation as `.venv/bin/pytest tests/test_trade_safety.py -q` (or `source .venv/bin/activate`) in CI/local docs to avoid false negatives.
2. Treat preflight exit 1 with only read-only FAIL as **expected** during safe/dry-run sessions; optional wrapper could distinguish “safe NO-GO” vs “broken infra.”
3. Before any live session, run `./pmx preflight` after explicit `./pmx go-live` only when the human intends to trade; keep read-only ON for agent/automation lanes by default.
4. Re-run `./pmx panic --dry-run` periodically to validate panic scope against current holdings without engaging the kill switch.

