---
name: pmxtrader-auto
description: >-
  Auto-route pmxtrader requests to Scout or Trader lane. Default Scout. Trader
  only for approved briefs or explicit execution. Use on Hermes Telegram without
  switching bundles.
---

# pmxtrader auto-routing

Pick **one lane per turn**. When ambiguous, use **Scout**.

## Lane selection

| Lane | Triggers |
|------|----------|
| **Scout** (default) | Research, quotes, links, compare, briefs, balance, status, preflight, paste URL, "what should I bet", "find a market", write/update brief |
| **Trader** | Brief has `approved: true` AND user wants to execute; OR user explicitly asks to trade/sell/close a market already in an approved brief |

## Lane rules

**Scout** — follow skill `pmxtrader-scout`:

- Terminal `./pmx` / `./pmx agent snapshot|discover|portfolio` for research
- May: link, quote, compare, brief, balance, status, portfolio snapshot
- Fill brief capability checklist + confidence / fair value
- **Never:** `./pmx trade`, `./pmx poly trade/sell/close`, `order:create`

**Trader** — follow skill `pmxtrader-trader`:

- Brief must have `approved: true` (or refuse and ask human to approve)
- Max **2** preparatory CLI calls before presenting order command
- Present exact `./pmx` command; ask **"Confirm to run?"**
- **Never** auto-execute live orders

## Telegram

- Optional one-line lane hint when switching: "Scout mode" or "Trader mode"
- Use `pmxtrader-telegram` for short mobile replies
- Never combine Scout research + Trader execution in one turn

## Explicit overrides

User may force a lane: "scout mode" / "trader mode" / `/pmxtrader-scout` / `/pmxtrader-trader`

Default bundle: `/pmxtrader` (this skill + both lane skills)
