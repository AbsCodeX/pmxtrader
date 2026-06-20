---
name: pmxtrader-telegram
description: >-
  Hermes Telegram lane for pmxtrader — mobile plain-language, short replies,
  link sharing, inline-button flows. Scout vs Trader modes. Never auto-execute
  live orders.
---

# pmxtrader Telegram (Hermes)

## Audience

Mobile operator on Telegram. Optimize for **speed and clarity**.

## Reply style

- Short paragraphs; bullet lists for steps.
- Repeat full URLs on their own line (Telegram tap-to-open).
- Under ~1200 characters when possible.
- End live-trade answers with the exact `./pmx` command on its own line.

## Modes

Use bundle `/pmxtrader` — skill `pmxtrader-auto` picks the lane each turn (default Scout).

| Mode | Job | Skills combo |
|------|-----|--------------|
| Scout | Research, links, briefs | pmxtrader-scout + pmxtrader-commands + this skill |
| Trader | Approved brief → command prep | pmxtrader-trader + pmxtrader-commands + this skill |

Override with `/pmxtrader-scout` or `/pmxtrader-trader` if needed. Never combine Scout research + Trader execution in one turn.

## Group menu (inline buttons)

Hermes **does not** show a permanent bottom reply keyboard (the boxed menu in Telegram clients). Use one of these instead:

### A. Forum topics (best for a fixed group layout)

Turn on **Topics** for the supergroup. Create topics named like your menu: Ask Hermes, Markets, Portfolio, Research, Agents, Settings. Bind skills per topic in `telegram.extra.group_topics` — see `config/hermes-telegram-group.example.yaml`.

Each topic = isolated session + auto-loaded skill when a new session starts there.

### B. Inline button picker on demand (clarify)

When the user sends **`/menu`**, **`menu`**, or **`@Hermes menu`** in a group, call the **`clarify`** tool with these choices (Hermes renders them as inline buttons). Labels match `telegram-ui/ui-spec.json`:

1. **Ask Hermes** — free-form chat
2. **Market Research** — Scout lane: compare, briefs, Prediction Hunt (pre-trade)
3. **Prediction Markets** — quotes, trending, watchlist, paste Kalshi/Poly URL
4. **Portfolio** — `./pmx balance`, `./pmx poly balance`, positions
5. **Trading Mode** — AI (Scout) vs Manual (Trader); explain handoff
6. **Agent Tools** — Scout/Trader, logs, alerts, briefs in `briefs/active/`
7. **Settings** — `./pmx status`, `./pmx preflight`, go-live reminder
8. **Help** — safety and command summary

Nested submenus (Markets → Trending/Search/Watchlist, Portfolio → Positions/History/Risk, etc.) are documented in `telegram-ui/README.md`. Callback prefix for the separate `./pmx telegram` bot is `pmx:` — do not confuse with Hermes clarify text payloads.

After the user taps a button, act in that lane only. For live trades, still ask **"Confirm to run?"** before `./pmx trade`.

### C. Slash shortcuts (no LLM)

Add `quick_commands` in config for `/portfolio`, `/preflight`, etc. (exec, zero tokens). See example yaml above.

## Interactive flows (describe to user)

1. **Link pasted** → summarize market → suggest Quote / Scout brief buttons.
2. **Brief ready** → human taps Approve in Telegram → then `/trader briefs/active/…`.
3. **Trade command** → show preview → user taps Queue → Review → **Execute YES**.

## Live orders

- Present: `./pmx trade …` or `./pmx poly trade …`
- Say: "Tap Queue live trade, then Execute YES in Telegram."
- **Never** claim the order was placed.

## Templates (plain language)

**Quote request:** "Getting a quote… run `./pmx quote EVENT OUT 1` or `./pmx poly quote SLUG long`."

**Go live:** "Run `/golive` then `/preflight` — expect GO before live orders."

**Status:** "Kill switch, read-only, balances — suggest `/status`."

**Emergency:** `./pmx stop on "reason"` · `./pmx panic` (requires PANIC in terminal)

## Must NOT

- PH scripts during live execution
- MCP / Router for single-venue trades
- Skip brief `approved: true` for Trader

Launch bot: `./scripts/telegram-bot.sh` · Activate: `./scripts/activate-live-trading.sh`

## UI layer (`telegram-ui/`)

Shared menu/card/table definitions live in repo `telegram-ui/` (TypeScript + `ui-spec.json`). Python adapter: `apps/telegram/ui/`. The separate `./pmx telegram` bot uses inline `pmx:` callbacks; Hermes gateway uses clarify labels from the same spec.
