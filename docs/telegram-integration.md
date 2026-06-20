# Telegram + Hermes live trading

Mobile control for pmxtrader via **Hermes gateway Telegram** (recommended) or an optional separate pmxtrader bot.

## Recommended: Hermes Telegram (you already have this)

If Hermes is already running on Telegram, wire pmxtrader into that profile — **do not** start a second bot.

```text
Telegram → Hermes gateway → terminal ./pmx → PMXT sidecar → Kalshi / Polymarket US
```

### One-time wiring

```bash
source scripts/pmxt-env.sh
./scripts/setup-hermes-telegram-profile.sh
# or: ./pmx hermes-telegram
```

This script:

1. Links pmxtrader skills into `~/.hermes/profiles/telegram/skills/prediction-markets/`
2. Syncs venue + LLM keys from `pmxt/.env` → `~/.hermes/profiles/telegram/.env`
3. Sets `terminal.cwd` to the pmxtrader repo and enables live terminal (`read_only: false`)
4. Refreshes `/pmxtrader` (auto-route), `/pmxtrader-scout`, and `/pmxtrader-trader` bundles

**Restart the Hermes Telegram gateway** after running the script so config and cwd take effect.

### Start a live session

On the machine where Hermes runs:

```bash
source scripts/pmxt-env.sh
./pmx activate-live          # warm + go-live + preflight (no --bot)
```

### In Telegram

| Action | How |
|--------|-----|
| Default (auto Scout/Trader) | `/pmxtrader` once, then plain language or paste a URL |
| Force research lane | `/pmxtrader-scout` |
| Force execution lane | Set `approved: true` in brief, then `/pmxtrader-trader` (or ask in `/pmxtrader` after approval) |
| Status / preflight | Ask in chat; agent runs `./pmx status` / `./pmx preflight` |
| Live trade | Agent presents exact `./pmx trade …` — **you confirm in chat** before it runs |

Plain-language examples:

- Paste a Kalshi or polymarket.us link
- `quote EVENT USA 1`
- `balance` / `preflight` / `status`

Bundles use `telegram-formatting` for short mobile-friendly replies.

## Group chat menu (inline buttons)

Hermes native Telegram does **not** attach a permanent bottom keyboard like some trading bots. You have three options:

### 1. Forum topics (recommended for a fixed group)

Enable **Topics** on your Hermes supergroup. Create topics matching your menu:

| Topic | pmxtrader lane | Skill binding |
|-------|----------------|---------------|
| Ask Hermes | Auto Scout/Trader | `pmxtrader-auto` |
| Markets | Quotes, links | `pmxtrader-scout` |
| Portfolio | Balances, positions | `pmxtrader-commands` |
| Research | Compare, briefs | `pmxtrader-scout` |
| Agents | Scout/Trader handoff | `multi-agent-handoff` |
| Settings | Status, preflight | `pmxtrader-commands` |

Add bindings under `telegram.extra.group_topics` in `~/.hermes/profiles/telegram/config.yaml`. Full example: `config/hermes-telegram-group.example.yaml`.

**Group setup checklist:**

1. BotFather → **Group Privacy → Turn off** (or always @mention the bot)
2. Add bot to group; promote if needed
3. `TELEGRAM_GROUP_ALLOWED_CHATS=-100…` in `~/.hermes/profiles/telegram/.env`
4. `telegram.require_mention: true` in config (mention or reply to bot)
5. Run `/pmxtrader` once in the group, then use topics or plain language

### 2. Inline picker on `/menu` (clarify buttons)

Say **`/menu`** or **`@YourBot menu`**. With the `pmxtrader-telegram` skill loaded, Hermes uses the **`clarify`** tool to show inline buttons: Markets, Portfolio, Research, Agents, Settings, Ask Hermes. Tapping a button routes that turn (same as choosing a menu item).

### 3. Quick slash commands (zero LLM)

```yaml
quick_commands:
  portfolio:
    type: exec
    command: cd /path/to/pmxtrader && ./pmx balance && ./pmx poly balance
```

Type `/portfolio` in the group — instant output, no model call.

**Note:** `telegram_module` in some configs is **not** stock Hermes; only built-in flows (`clarify`, `/model`, approvals) and the patterns above provide inline buttons unless you run the separate `./pmx telegram` bot (UI layer in `telegram-ui/` + `apps/telegram/ui/`).

## UI layer (`telegram-ui/`)

Repo folder `telegram-ui/` defines menus, cards, tables, Mini App URLs, and `pmx:` callback naming. Python adapter: `apps/telegram/ui/`. Tests: `pytest tests/test_telegram_ui.py`.

| Path | Hermes gateway | `./pmx telegram` |
|------|----------------|------------------|
| Menus | `clarify` labels from skill + `ui-spec.json` | Inline keyboards via Python adapter |
| Trades | Confirm in chat before `./pmx trade` | Queue → Review → Confirm execute |
| Mini Apps | Optional WebApp URLs in env | `PMX_TELEGRAM_MINIAPP_*` buttons |

Env: `PMX_TELEGRAM_GROUP_TRADING`, `TELEGRAM_ADMIN_CHAT_IDS`, `PMX_TELEGRAM_MINIAPP_*` — see `pmxt/.env.example` and `telegram-ui/README.md`.

## Optional: separate pmxtrader bot (`./pmx telegram`)

Only use this if you want a **dedicated** Telegram bot with inline **Queue → Execute YES** buttons (not Hermes gateway).

```text
Telegram → pmxtrader bot → Hermes subprocess → ./pmx CLI → venues
```

Setup requires `@BotFather` token + `TELEGRAM_BOT_TOKEN` / `TELEGRAM_ALLOWED_CHAT_IDS` in `pmxt/.env`:

```bash
pip install -r requirements-telegram.txt
./scripts/setup-hermes.sh
./pmx activate-live --bot
```

See `scripts/telegram-bot.sh` and `apps/telegram/` for implementation.

## Safety (both paths)

1. **Kill switch** — `./pmx stop on` blocks new trades
2. **`./pmx go-live`** — read-only off for the session
3. **Brief `approved: true`** — Trader gate (Scout never orders)
4. **Human confirm** — Hermes Telegram: confirm in chat; separate bot: Queue + Execute YES token (5 min)
5. **Audit log** — same as terminal (`trade_safety_audit_log`)

Emergency: `./pmx stop on "reason"` or `./pmx panic` (PANIC confirm stays in terminal for panic).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `./pmx` not found in Hermes | Re-run `./scripts/setup-hermes-telegram-profile.sh`; restart gateway |
| READ-ONLY blocked | `./pmx activate-live` on the Hermes host |
| Scout places orders | Use `/pmxtrader` (defaults Scout) or `/pmxtrader-scout`; Trader needs approved brief |
| Wrong working directory | Check `terminal.cwd` in `~/.hermes/profiles/telegram/config.yaml` |
| Second bot conflicts | Stop `./pmx telegram`; use Hermes gateway only |

See also: `docs/multi-agent.md` · `hermes/README.md` · `docs/commands.md`
