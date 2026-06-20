# Known risks and limitations

Last reviewed: **2026-06-19** (Batch K — see `reviews/2026-06-19/documentation-review.md`).

Read this before live trading or deploying agents.

---

## Real money

- `./pmx trade`, `./pmx poly trade|sell|close`, and `./pmx panic` move **real funds** when venue keys are configured.
- There is **no automated daily loss limit** — use brief `max-loss`, `./pmx stop`, and manual discipline.
- Failed orders **do not auto-repeat**; emergency GET retries (429/503) are not order retries.

---

## Execution surfaces

| Surface | Live orders? |
|---------|--------------|
| Terminal `./pmx` | Yes (when kill switch OFF and not read-only) |
| Cockpit TUI | Yes — **ConfirmCommandModal** required |
| Web dashboard | **No** — trades blocked by design |
| Scout agent | **No** — read-only policy |
| Trader agent | Prepares commands; human runs `./pmx trade` |

---

## Safety controls

| Control | Limitation |
|---------|------------|
| Kill switch (`./pmx stop`) | Blocks **new** trades; does not undo filled orders |
| `PMX_READ_ONLY=1` | Env-level block; easy to forget if unset |
| `PMX_MAX_TRADE_CONTRACTS` | Per-order cap only, not portfolio exposure |
| Dry-run (`--dry-run`, `PMX_DRY_RUN`) | Scripts only — verify flags before live session |

Full audit: `reviews/2026-06-19/trading-safety-review.md`

---

## Agents and MCP

- **Grok + PMXT MCP** causes schema errors — Hermes setup disables trading MCP by default.
- Scout/Trader should use **terminal `./pmx`**, not MCP, for live venue actions.
- LLM output can be wrong — always verify quotes with `./pmx quote` before trading.
- Trader requires `approved: true` in brief frontmatter; still needs human confirmation in cockpit or manual `./pmx`.

---

## Sidecar and infrastructure

- PMXT sidecar **replaces** a manually started dev server when CLI/SDK runs (`~/.pmxt/server.lock`).
- Committed `pmxt/node_modules` may contain **macOS arm64** binaries — run `npm --prefix pmxt install` on Linux (do not commit resulting changes).
- Git submodules `pmxt-mcp/`, `molt-pmxt/` need `git submodule update --init`.
- CI does **not** call live venue APIs — production behavior requires manual `./pmx warm` testing.

---

## Security

- Dashboard binds **127.0.0.1** by default; wide bind requires `PMXT_DASHBOARD_INSECURE_BIND=1`.
- Never commit `pmxt/.env`, `KILL_SWITCH`, or `briefs/active/` contents.
- Pre-commit and CI scan for common secret patterns — not a guarantee.

---

## Documentation gaps (accepted)

| Gap | Mitigation |
|-----|------------|
| Root npm `build`/`lint` not functional | Use Python CI + `pmxt-core` build (`AGENTS.md`) |
| No E2E Hermes test in CI | Manual `./pmx scout grok` with keys |
| Order book streaming not UI-tested | Terminal `./pmx watch` by design |
