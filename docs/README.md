---
hide:
  - toc
---

<div class="pmx-hero pmx-glass" markdown="1">

# pmxtrader

<p class="pmx-lead">
Human-gated prediction market operations for <strong>Kalshi</strong> and <strong>Polymarket US</strong>.
Terminal-first execution, layered safety defaults, and venue adapters powered by PMXT.
</p>

<div class="pmx-pill-row">
  <span class="pmx-pill pmx-pill--green">Read-only by default</span>
  <span class="pmx-pill pmx-pill--blue">Kalshi · Polymarket US</span>
  <span class="pmx-pill pmx-pill--orange">Real money after go-live</span>
</div>

</div>

<div class="grid cards" markdown="1">

-   :material-rocket-launch-outline:{ .lg .middle } **Start a session**

    ---

    Bootstrap the sidecar, check balances, and confirm safety posture before any trade prep.

    [:octicons-arrow-right-24: Command reference](commands.md#start-a-session){ .md-button }

-   :material-shield-check-outline:{ .lg .middle } **Before live money**

    ---

    Review risks, environment defaults, and the preflight checklist. Sessions stay read-only until you explicitly go live.

    [:octicons-arrow-right-24: Known risks](known-risks.md){ .md-button }

-   :material-chart-timeline-variant:{ .lg .middle } **Venue playbooks**

    ---

    Kalshi event IDs, Poly US slugs, panic flatten, and venue-specific credential setup.

    [:octicons-arrow-right-24: Kalshi](kalshi-integration.md){ .md-button }
    [:octicons-arrow-right-24: Polymarket US](polymarket-us-integration.md){ .md-button }

</div>

## Live session checklist

<div class="pmx-checklist" markdown="1">

<div class="pmx-checklist__head">Recommended operator flow</div>

1. **`./pmx session`** — warm sidecar; session starts read-only (`PMX_READ_ONLY=1`).
2. **`./pmx preflight`** — expect **NO-GO** until you intentionally enable live trading.
3. **`./pmx preview trade …`** or **`./pmx preview poly trade …`** — quote and intent only; no order sent.
4. **`./pmx go-live`** — clears read-only; re-run **`./pmx preflight`** and expect **GO**.
5. **`./pmx trade …`** — terminal prompts **YES** before `order:create` (unless `--yes`).

</div>

!!! warning "Web dashboard is not an execution surface"
    `./pmx dashboard` is for read-only analysis and copying commands into Terminal.
    Live orders belong in Terminal or Cockpit with explicit confirmation.

<div class="pmx-stats" markdown="1">

<div class="pmx-stat" markdown="1">
<div class="pmx-stat__label">Terminal CLI</div>
<div class="pmx-stat__value">`./pmx` — primary execution path</div>
</div>

<div class="pmx-stat" markdown="1">
<div class="pmx-stat__label">Cockpit TUI</div>
<div class="pmx-stat__value">`./pmx cockpit` — confirm modal on trades</div>
</div>

<div class="pmx-stat" markdown="1">
<div class="pmx-stat__label">PMXT sidecar</div>
<div class="pmx-stat__value">`:3847` · credentials in `pmxt/.env`</div>
</div>

<div class="pmx-stat" markdown="1">
<div class="pmx-stat__label">Agents</div>
<div class="pmx-stat__value">Scout research · Trader prepares · human executes</div>
</div>

</div>

## Surfaces at a glance

| Surface | Entry | Can place live orders? |
|---------|-------|----------------------|
| **Terminal** | `./pmx` | Yes — after `./pmx go-live` + YES confirm |
| **Cockpit** | `./pmx cockpit` | Yes — confirm modal required |
| **Dashboard** | `./pmx dashboard` | **No** — copy commands to Terminal |
| **Scout** | `./pmx scout` | **No** — research only |
| **Trader** | `./pmx trader` | Prepares commands; human runs them |

## Documentation map

<div class="grid cards" markdown="1">

-   :material-book-open-page-variant-outline:{ .lg .middle } **Operations**

    ---

    Commands, environment variables, cockpit, multi-agent workflow, LLM routing.

    [Commands](commands.md) · [Environment](environment.md) · [Multi-agent](multi-agent.md)

-   :material-source-branch:{ .lg .middle } **Engineering**

    ---

    Architecture, repo layout, CI/testing, dependency inventory, decision log.

    [Architecture](architecture.md) · [Structure](project-structure.md) · [Testing](testing.md)

-   :material-clipboard-check-outline:{ .lg .middle } **Reports & audit**

    ---

    Live readiness, dry-run verification, official venue links.

    [Live readiness](reports/live-readiness.md) · [Dry-run test](reports/dry-run-test.md) · [Official links](official-links.md)

</div>

??? note "Reference diagrams"
    ### Choose your path

    ```mermaid
    flowchart TD
      A[New to pmxtrader?] --> B{Goal?}
      B -->|Install & run| C[Command reference]
      B -->|Env vars & safety| D[Environment]
      B -->|Risks before live| E[Known risks]
      B -->|Repo layout| F[Project structure]
      C --> G[./pmx preflight]
      G --> H{Live trading?}
      H -->|No| I[preview / dashboard / scout]
      H -->|Yes| J[go-live → preflight GO → trade]
    ```

    ### Live session sequence

    ```mermaid
    sequenceDiagram
      participant You
      participant pmx as ./pmx
      participant Sidecar as PMXT sidecar
      participant Venue as Kalshi / Poly US

      You->>pmx: session / warm
      pmx->>Sidecar: health check
      You->>pmx: preflight
      Note over You,pmx: NO-GO while read-only
      You->>pmx: preview trade …
      You->>pmx: go-live
      You->>pmx: preflight
      Note over You,pmx: GO
      You->>pmx: trade … + YES
      pmx->>Sidecar: order:create
      Sidecar->>Venue: signed request
    ```

    ### Safety layers

    ```mermaid
    flowchart TB
      subgraph UI["Layer 1 — UI"]
        D[Dashboard<br/>trades blocked]
        C[Cockpit<br/>confirm modal]
        T[Terminal<br/>YES prompt]
      end
      subgraph Env["Layer 2 — Session"]
        R[PMX_READ_ONLY default]
        K[Kill switch]
        M[Max contracts cap]
        P[preflight / sidecar gate]
      end
      subgraph Agent["Layer 3 — Agents"]
        S[Scout read-only]
        B[Brief approved: true]
      end
      UI --> Env --> Agent --> Order[order:create]
    ```

## Config vs secrets

| Location | Contains | In git? |
|----------|----------|---------|
| `pmxt/.env` | Venue + LLM API keys | **No** |
| `config/agents.json` | Scout/Trader policy | Yes |
| `config/providers.json` | Model defaults | Yes |
| `KILL_SWITCH` | Halt sentinel file | **No** |
| `.pmx-live` | Go-live marker | **No** |
| `briefs/active/` | Trade briefs | **No** |

## Venues

| Venue | CLI prefix | Demo / preview |
|-------|------------|----------------|
| **Kalshi** | `./pmx` | `./scripts/kalshi-demo-quickstart.sh` |
| **Polymarket US** | `./pmx poly` | `./pmx preview poly trade …` only |

Other PMXT exchanges live under `pmxt/` but are not wired to `./pmx` shortcuts today.

---

**Local preview:** `pip install -r requirements-docs.txt && ./scripts/docs-serve.sh` → [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Repository:** [github.com/AbsCodeX/pmxtrader](https://github.com/AbsCodeX/pmxtrader)
