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

| Mode | Job | Skills combo |
|------|-----|--------------|
| Scout | Research, links, briefs | pmxtrader-scout + pmxtrader-commands + this skill |
| Trader | Approved brief → command prep | pmxtrader-trader + pmxtrader-commands + this skill |

Never combine Scout research + Trader execution in one turn.

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
