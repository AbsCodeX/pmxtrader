---
description: Real-money risks, execution surfaces, safety controls, and accepted gaps.
---

<div class="pmx-page-hero" markdown="1">

# Known risks

<p class="pmx-page-lead">
Read this before live trading or deploying agents. pmxtrader defaults to read-only sessions;
real orders require an explicit <code>./pmx go-live</code> and operator confirmation.
</p>

</div>

## Decision flow

??? note "Go-live decision diagram"
    ```mermaid
    flowchart TD
      Start[Start session] --> RO{Read-only ON?}
      RO -->|default yes| Safe[Safe: preview, research, dashboard]
      RO -->|./pmx go-live| GL[Live mode enabled]
      GL --> PF[./pmx preflight GO?]
      PF -->|no| Fix[Fix sidecar / keys / kill switch]
      PF -->|yes| Prev[Optional: preview trade]
      Prev --> Trade[./pmx trade + YES]
      Trade --> Live[Real money at venue]
    ```

---

## Real money

| Risk | Detail |
|------|--------|
| Live orders | `./pmx trade`, `./pmx poly trade/sell/close` use real funds after go-live |
| Panic | `./pmx panic` flattens Kalshi + Poly US when keys present |
| Daily loss cap | Set `PMX_MAX_DAILY_LOSS` — wired into `./pmx preflight` and `./pmx risk status` |
| No auto-retry on failed POST | Failed orders are not repeated |

---

## Execution surfaces

| Surface | Live orders? | Guard |
|---------|--------------|-------|
| Terminal `./pmx` | Yes (after go-live) | YES prompt, preflight, kill switch |
| Cockpit TUI | Yes | ConfirmCommandModal |
| Web dashboard | **No** | Command allowlist |
| Scout agent | **No** | `config/agents.json` |
| Trader agent | Prepares only | `approved: true` + human runs trade |

??? note "Execution surface diagram"
    ```mermaid
    flowchart LR
      subgraph Safe["No live orders"]
        D[Web dashboard]
        S[Scout agent]
      end
      subgraph Guarded["Live with guards"]
        C[Cockpit + confirm]
        T[Terminal + YES]
      end
      subgraph Indirect["Human executes"]
        TR[Trader agent → you run ./pmx]
      end
      Safe --> Research[Research / preview]
      Guarded --> Live[order:create]
      Indirect --> Live
    ```

---

## Safety controls

| Control | What it does | Limitation |
|---------|--------------|------------|
| `./pmx preflight` | GO/NO-GO checklist | Exit **1** is expected in read-only; **2** means fix sidecar/keys |
| `PMX_READ_ONLY=1` | Blocks live trades | Default ON; cleared by `./pmx go-live` |
| Kill switch | Blocks new trades | Does not undo fills |
| `PMX_MAX_TRADE_CONTRACTS` | Per-order cap (default 10) | Not portfolio exposure |
| `PMX_MAX_DAILY_LOSS` | Blocks new trades when today's ledger exceeds cap | Requires ledger updates via `./pmx risk` / trade P&L recording |
| Trade confirm | Type YES | Skipped with `--yes` / `PMX_TRADE_CONFIRM=0` |
| Dry-run / preview | No `order:create` | Script-level only |
| `./pmx panic --dry-run` | Preview flatten scope | One venue API failure logs warning and continues |
| Trade audit | `briefs/alerts/trades.jsonl` | Cockpit **Audit** tab (key `8`) tails jsonl logs |

Full audit: [trading-safety review](https://github.com/AbsCodeX/pmxtrader/blob/main/reviews/2026-06-19/trading-safety-review.md)

---

## Agents and MCP

| Topic | Guidance |
|-------|----------|
| Grok + PMXT MCP | Disabled by default (schema errors) |
| Execution path | Terminal `./pmx`, not MCP |
| LLM accuracy | Verify with `./pmx quote` before trading |
| Trader brief | Requires `approved: true` in frontmatter |

---

## Sidecar and infrastructure

| Topic | Risk |
|-------|------|
| Sidecar replacement | CLI replaces manual dev server (`~/.pmxt/server.lock`) |
| `pmxt/node_modules` | Not in git — run `npm --prefix pmxt install` after clone (Linux vs macOS binaries) |
| Submodules | `git submodule update --init --recursive` for MCP; pmxt submodule planned — see [`pmxt-submodule-migration.md`](pmxt-submodule-migration.md) |
| CI | Installs pmxt deps + builds pmxt-core; no live venue tests |

---

## Security

| Topic | Rule |
|-------|------|
| Dashboard bind | `127.0.0.1` default; wide bind needs `PMXT_DASHBOARD_INSECURE_BIND=1` |
| Never commit | `pmxt/.env`, `KILL_SWITCH`, `briefs/active/` |
| Secret scan | Pre-commit + CI — not a guarantee |

---

## Accepted gaps

| Gap | Mitigation |
|-----|------------|
| pmxt not yet a submodule | Vendored tree + migration doc [`pmxt-submodule-migration.md`](pmxt-submodule-migration.md) |
| PMXT npm audit debt | Partial ws bump + `npm audit fix`; ethers v6 / viem chain deferred — see [`dependencies.md`](dependencies.md) |
| No Hermes E2E in CI | Manual agent testing |
| Order book not UI-tested | `./pmx watch` in Terminal |
| No Poly US demo venue | Use `./pmx preview poly` |
