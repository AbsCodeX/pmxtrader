# Trading safety review — 2026-06-19

**Linear parent:** [ABI-72](https://linear.app/pmxt/issue/ABI-72/trading-safety-review-2026-06-19)  
**Sub-issues:** ABI-73–ABI-78  
**Module:** `apps/bridge/trade_safety.py`, `scripts/trade-safety-lib.sh`

Related: [ABI-5](https://linear.app/pmxt/issue/ABI-5) cockpit/dashboard security, [ABI-65](https://linear.app/pmxt/issue/ABI-65) functionality review

---

## Checklist (audit criteria)

| Criterion | Verdict | Mechanism |
|-----------|---------|-----------|
| No accidental live trades | **Pass** | Web dashboard blocks trades; cockpit confirm modals; Terminal-only execution paths |
| Read-only mode available | **Pass** | Kill switch ON; `PMX_READ_ONLY=1`; web dashboard; Scout agent read-only (`config/agents.json`) |
| Dry-run mode available | **Pass (after Batch I)** | `./pmx stop dry`; `kill-switch.sh stop --dry-run`; `--dry-run` / `PMX_DRY_RUN=1` on live trade scripts |
| Manual approval required | **Pass** | Cockpit `ConfirmCommandModal`; Trader brief `approved: true`; PANIC typing; humanGate in `config/agents.json` |
| Max trade size enforced | **Pass (after Batch I)** | `PMX_MAX_TRADE_CONTRACTS` checked in Kalshi/Poly trade paths |
| Loss limits enforced | **Partial** | No automated daily PnL stop — operator uses brief max-loss + `./pmx stop` (documented) |
| Kill switch exists | **Pass** | `KILL_SWITCH` file sentinel; checked before every live trade |
| Failed trades do not auto-repeat | **Pass** | Single `order:create` per invocation; emergency GET retry only (429/503), not failed POST orders |

---

## Safety layers (defense in depth)

```
Layer 1 — UI/API
  Web dashboard: resolve_dashboard_command() denylist (no trade/scout)
  Cockpit palette: allowlist (safe reads only)
  Cockpit AI: ConfirmCommandModal before exec

Layer 2 — File / env gates
  KILL_SWITCH file → kill_switch_require_clear()
  PMX_READ_ONLY=1 → trade_safety_require_live()
  PMX_MAX_TRADE_CONTRACTS → trade_safety_check_amount()

Layer 3 — Agent policy
  Scout: no order:create (config/agents.json)
  Trader: requires approved brief + max 2 CLI calls + human confirm

Layer 4 — Emergency
  ./pmx stop | panic | kill-switch.sh stop [--dry-run] [--cash-out]
```

---

## Controls reference

| Control | How to use |
|---------|------------|
| Kill switch | `./pmx stop on "reason"` · `./pmx resume` · `./pmx status` |
| Read-only env | `export PMX_READ_ONLY=1` (blocks live trades even if switch OFF) |
| Max size | `export PMX_MAX_TRADE_CONTRACTS=10` |
| Dry-run trade | `./pmx trade MKT OUT 1 --dry-run` · `./pmx poly trade SLUG long 1 --dry-run` · `PMX_DRY_RUN=1` |
| Panic dry-run | `./pmx stop dry` (preview flatten) |
| Trader gate | Brief frontmatter `approved: true` required |

---

## Fixes applied (Batch I)

| Linear | Fix |
|--------|-----|
| [ABI-73](https://linear.app/pmxt/issue/ABI-73) | `apps/bridge/trade_safety.py` + `trade-safety-lib.sh` |
| [ABI-74](https://linear.app/pmxt/issue/ABI-74) | `PMX_READ_ONLY=1` blocks live trades |
| [ABI-75](https://linear.app/pmxt/issue/ABI-75) | `--dry-run` / `PMX_DRY_RUN` on Kalshi + Poly trade scripts |
| [ABI-76](https://linear.app/pmxt/issue/ABI-76) | `PMX_MAX_TRADE_CONTRACTS` enforced before order:create |
| [ABI-77](https://linear.app/pmxt/issue/ABI-77) | `tests/test_trade_safety.py` — guards + no-retry verification |
| [ABI-78](https://linear.app/pmxt/issue/ABI-78) | Review mirror (this file + `linear-task-safety.md`) |

---

## Remaining gaps (accepted)

| Gap | Severity | Mitigation |
|-----|----------|------------|
| No automated daily loss limit | Medium | Brief `max_loss` field + manual `./pmx stop`; future: PnL ledger hook |
| Kalshi trade has no interactive confirm in script | Low | Use cockpit Safety tab or review `--dry-run` first |
| PMXT vendor retry policy | Info | pmxtrader scripts do not auto-retry failed orders |

---

## Progress

| Batch | Issues | Done |
|-------|--------|------|
| Batch I | 6 (ABI-73–ABI-78) | 6 |
| **Parent ABI-72** | **6 sub-issues** | **6** |
