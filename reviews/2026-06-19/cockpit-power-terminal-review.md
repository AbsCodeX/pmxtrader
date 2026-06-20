# Cockpit Power Terminal Review — 2026-06-19

## Executive summary

Audited the Textual cockpit (`apps/cockpit/`) and web dashboard balance parsing. Fixed a **critical data wiring bug** where Poly US displayed Kalshi cash. Applied a terminal trading-desk UI overhaul (compact density, high-contrast palette) and parallelized live data fetches.

---

## Findings

### 1. Poly US showing Kalshi balances (FIXED)

**Root cause:** `parse_status()` in `apps/bridge/parse.py` used unanchored regex:

```python
Polymarket US:[\s\S]*?available:
```

`./pmx status` emits panic-scope lines *before* balance blocks:

```
  Kalshi: included
  Polymarket US: included    ← first "Polymarket US:" match

Kalshi:
  available: 100.50           ← first "available:" after that match
```

The Poly regex matched panic-scope `Polymarket US: included` and captured Kalshi's `available:` value.

**Fix:**
- Anchored balance regex to column-0 section headers (`^Kalshi:` / `^Polymarket US:` + newline + indented `available:`).
- Added `parse_balance_json()` for direct venue API output.
- `fetch_snapshot()` now parallel-fetches `./pmx balance` and `./pmx poly balance`; direct JSON overrides status parse (fallback when keys/sidecar unavailable).
- Same regex fix applied to `dashboard/js/app.js`.

### 2. UI/UX — bulky, dull, slow (IMPROVED)

| Issue | Change |
|-------|--------|
| Washed GitHub-gray palette | Terminal palette: `#050608` bg, `#00ff9c` green, `#00d4ff` cyan, `#ffb000` amber |
| Tall stat bar (height 3) | Compact 2-line cells with abbreviated labels (KAL/POLY/MKT) |
| 12s refresh | 8s poll interval; parallel status + balances + positions |
| Light inputs/modals on dark shell | Dark terminal inputs, command palette, confirm modal |
| Wide nav (22 cols) | 20 cols, 1-line items, green highlight |

**Patterns applied:** btop++/htop high-contrast dark terminal, lazygit compact borders, Bloomberg-style stat cells, Rich/Textual 8.x `Text` for safe log writes (already fixed in `output_log.py`).

### 3. Performance (IMPROVED)

- `fetch_snapshot`: status + Kalshi/Poly balances in parallel (`ThreadPoolExecutor`).
- `_positions_preview`: Kalshi + Poly positions in parallel.
- `_health_checks` full probe: balance calls in parallel.
- Heavy health API probes still throttled (`HEAVY_HEALTH_EVERY = 3`).

**Trade-off:** Two extra subprocess calls per refresh (direct balance fetches) — intentional for venue correctness; status parse alone was unreliable.

### 4. Architecture notes

```
CockpitApp.poll_live (8s)
  └─ fetch_dashboard (worker thread)
       ├─ fetch_snapshot
       │    ├─ parallel: status + (balance, poly balance)
       │    └─ optional: poly markets
       ├─ parallel: kalshi positions + poly positions
       └─ health checks (light or heavy every 3rd poll)
```

Web dashboard (`dashboard/`) shares parse logic via JS — regex fix only; no CSS overhaul in this pass.

---

## Files changed

| File | Change |
|------|--------|
| `apps/bridge/parse.py` | Anchored regex, `parse_balance_json()` |
| `apps/cockpit/bridge/live.py` | Parallel fetches, balance apply/fallback |
| `apps/cockpit/theme.tcss` | Terminal palette, dark inputs |
| `apps/cockpit/widgets/stats_bar.py` | Compact stat cells |
| `apps/cockpit/widgets/ticker_bar.py` | Terminal ticker strip |
| `apps/cockpit/widgets/activity_log.py` | Shorter dock height |
| `apps/cockpit/widgets/nav.py` | Compact sidebar |
| `apps/cockpit/widgets/sparkline.py` | Terminal price colors |
| `apps/cockpit/screens/home.py` | Module styling, balance panel |
| `apps/cockpit/app.py` | 8s refresh, dark palette modal |
| `dashboard/js/app.js` | Anchored balance regex |
| `tests/test_bridge.py` | Panic-scope parse tests |
| `tests/test_functionality.py` | Venue separation tests |
| `tests/test_cockpit_bridge.py` | Parallel balance test |

---

## Tests

```bash
python3 -m pytest tests/ -q          # full suite
python3 -m ruff check apps/cockpit  # cockpit lint
```

New coverage:
- `test_parse_status_ignores_panic_scope_lines` — Poly ≠ Kalshi from status text
- `test_fetch_snapshot_venue_separation_from_direct_api` — direct API isolation
- `test_fetch_balances_parallel_returns_separate_venues`

---

## Remaining recommendations

1. **Web dashboard styling** — align `dashboard/css/app.css` with cockpit terminal palette.
2. **Balance cache TTL** — 2–3s in-memory cache if 8s poll + 3 subprocess calls feels heavy on cold sidecar.
3. **Markets fetch decoupling** — fetch top markets every N polls, not every refresh.
4. **Textual CSS variables** — centralize `#00ff9c` / `#00d4ff` tokens in one theme module.
5. **Live sparkline history** — persist history file already exists; expose timeframe selector in UI.
