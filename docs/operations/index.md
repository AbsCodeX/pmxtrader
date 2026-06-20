---
description: Operator guide — sessions, safety, commands, cockpit, and agent workflow.
hide:
  - toc
---

<div class="pmx-page-hero pmx-glass" markdown="1">

# Operations

<p class="pmx-page-lead">
Run pmxtrader safely: bootstrap sessions, verify preflight, preview orders, and execute only when you intend to.
Kalshi and Polymarket US share the same safety stack.
</p>

<div class="pmx-pill-row">
  <span class="pmx-pill pmx-pill--green">Read-only default</span>
  <span class="pmx-pill pmx-pill--blue">Terminal-first execution</span>
  <span class="pmx-pill">Last reviewed 2026-06-20</span>
</div>

</div>

## Session checklist

<div class="pmx-checklist pmx-glass" markdown="1">

<div class="pmx-checklist__head">Standard operator flow</div>

1. **`./pmx session`** — warm sidecar; read-only ON.
2. **`./pmx preflight`** — expect **NO-GO** until go-live.
3. **`./pmx preview trade …`** — quote + intent; no order.
4. **`./pmx go-live`** — enable live mode; re-run preflight for **GO**.
5. **`./pmx trade …`** — confirm **YES** at the prompt.

</div>

<div class="grid cards" markdown="1">

-   :material-console-line:{ .lg .middle } **Command reference**

    ---

    Full `./pmx` surface: Kalshi, Polymarket US, safety, Hermes bundles.

    [:octicons-arrow-right-24: Commands](../commands.md)

-   :material-tune-variant:{ .lg .middle } **Environment & safety**

    ---

    `pmxt/.env` credentials, `PMX_READ_ONLY`, caps, preflight gates.

    [:octicons-arrow-right-24: Environment](../environment.md)

-   :material-alert-decagram-outline:{ .lg .middle } **Known risks**

    ---

    Real-money surfaces, agent limits, accepted gaps before live trading.

    [:octicons-arrow-right-24: Risks](../known-risks.md)

-   :material-monitor-dashboard:{ .lg .middle } **Cockpit TUI**

    ---

    Textual dashboard: balances, safety tab, confirm modals on mutating actions.

    [:octicons-arrow-right-24: Cockpit](../cockpit.md)

-   :material-account-group-outline:{ .lg .middle } **Multi-agent workflow**

    ---

    Scout research → approved brief → Trader command prep → human execution.

    [:octicons-arrow-right-24: Multi-agent](../multi-agent.md)

-   :material-api:{ .lg .middle } **LLM providers**

    ---

    Grok, Claude, OpenAI routing via Hermes; keys and budget guidance.

    [:octicons-arrow-right-24: Providers](../providers.md)

</div>

## Execution surfaces

| Surface | Entry | Live orders? | Primary guard |
|---------|-------|--------------|---------------|
| Terminal | `./pmx` | After `./pmx go-live` | YES prompt · preflight · kill switch |
| Cockpit | `./pmx cockpit` | Yes | Confirm modal · Safety tab for panic |
| Dashboard | `./pmx dashboard` | **No** | Allowlist; copy to Terminal |
| Scout | `./pmx scout` | **No** | Research-only policy |
| Trader | `./pmx trader` | **No** | Prepares commands; you execute |

!!! tip "Venue playbooks"
    Kalshi and Polymarket US have dedicated integration guides under the **Venues** tab.

??? note "Session mode diagram"
    ```mermaid
    flowchart LR
      A[session] --> B[preflight]
      B --> C{go-live?}
      C -->|no| D[preview / dashboard / scout]
      C -->|yes| E[preflight GO]
      E --> F[trade + YES]
    ```
