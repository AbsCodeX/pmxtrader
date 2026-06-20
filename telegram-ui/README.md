# pmxtrader Telegram UI layer

This folder is named **`telegram-ui/`** (not `telegram/`) to avoid shadowing the `python-telegram-bot` `telegram` package when the repo root is on `PYTHONPATH`.

This folder does **not** replace Hermes core (`~/.hermes/hermes-agent`). It provides:

- Menu trees and callback naming (`pmx:` prefix)
- Card and table message formatters
- Mini App URL placeholders
- Permission rules (admin, group trading flag)

## Layout

| File | Role |
|------|------|
| `bot.ts` | Orchestration helpers |
| `menus.ts` | Main + nested menus |
| `keyboards.ts` | Inline keyboard shapes |
| `cards.ts` | Markdown card templates |
| `tables.ts` | Monospace tables |
| `callbacks.ts` | `pmx:` callback builders |
| `miniapps.ts` | WebApp URLs from env |
| `permissions.ts` | Chat/admin/group trading |
| `ui-spec.json` | Runtime spec for Python |

## Python runtime

`apps/telegram/ui/` loads `ui-spec.json` and builds `python-telegram-bot` markup. Wired from `apps/telegram/bot.py` and `apps/telegram/keyboards.py`.

## Hermes gateway (recommended)

Stock Hermes has no persistent reply keyboard. Use:

1. **`/menu`** — Hermes `clarify` tool with labels from `ui-spec.json` main menu (see `hermes/skills/pmxtrader-telegram/SKILL.md`)
2. **Forum topics** — one topic per section
3. **Separate bot** — `./pmx telegram` uses this UI layer directly

## Env vars (add to `pmxt/.env`)

```bash
PMX_TELEGRAM_GROUP_TRADING=0          # 1 to allow live trades in groups
TELEGRAM_ADMIN_CHAT_IDS=              # optional; defaults to TELEGRAM_ALLOWED_CHAT_IDS
PMX_TELEGRAM_MINIAPP_DASHBOARD=
PMX_TELEGRAM_MINIAPP_TERMINAL=
PMX_TELEGRAM_MINIAPP_PORTFOLIO=
PMX_TELEGRAM_MINIAPP_RESEARCH=
PMX_TELEGRAM_MINIAPP_AGENTS=
PMX_TELEGRAM_MINIAPP_SETTINGS=
```

## Typecheck (optional)

```bash
cd telegram-ui && npm install && npm run typecheck
```

## Safety

- Live trades: **Queue → Review → Confirm execute** (never one button)
- Group chats: trading blocked unless `PMX_TELEGRAM_GROUP_TRADING=1`
- Callback prefix `pmx:` keeps UI routes separate from legacy `act:` / `trade:` handlers

## Sync

When editing TypeScript menus/keyboards, update `ui-spec.json` to match. CI tests in `tests/test_telegram_ui.py` validate structure and Python adapter behavior.
