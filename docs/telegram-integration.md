# Telegram + Hermes live trading

Mobile control for pmxtrader: plain-language chat with Hermes, inline buttons for brief approval and live orders, link parsing for Kalshi / Polymarket US URLs.

## Architecture

```text
Telegram (you) → pmxtrader bot → Hermes (Scout/Trader skills) → ./pmx CLI → PMXT sidecar → venues
```

- **Scout mode** (default): research, quotes, briefs — no orders.
- **Trader mode**: approved brief only — presents exact `./pmx` commands.
- **Live orders**: Queue → Review preview → **Execute YES** (one-time token; still requires `./pmx go-live`).

Telegram does **not** bypass kill switch, read-only mode, contract caps, or brief approval.

## One-time setup

### 1. Create a Telegram bot

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
2. Message [@userinfobot](https://t.me/userinfobot) → copy your numeric **chat id**.

### 2. Configure `pmxt/.env`

```bash
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_ALLOWED_CHAT_IDS=YOUR_CHAT_ID
TELEGRAM_HERMES_PROVIDER=grok
```

Only allowlisted chat IDs can use the bot.

### 3. Hermes + skills

```bash
pip install hermes-agent python-telegram-bot
./scripts/setup-hermes.sh
./scripts/install-hermes-skills.sh   # includes pmxtrader-telegram skill
pip install -r requirements-telegram.txt
```

### 4. Venue keys

Add Kalshi and/or Polymarket US keys to `pmxt/.env` (see `docs/environment.md`).

## Start a live session

```bash
source scripts/pmxt-env.sh
./pmx activate-live          # warm + go-live + preflight
./pmx telegram               # foreground bot (Ctrl+C to stop)
```

Or combined:

```bash
./pmx activate-live --bot
```

## Plain-language usage

| You send | Bot does |
|----------|----------|
| `/start` | Menu: Status, Scout/Trader mode, Briefs, Go live |
| Paste a market URL | Scout summary + quote buttons |
| `quote EVENT USA 1` | Runs `./pmx quote …` |
| `/scout Fed rate market` | Hermes research (fast Grok) |
| `/briefs` | List briefs → **Approve** button |
| `/trader briefs/active/DATE-slug.md` | Trader prep from approved brief |
| Hermes returns `./pmx trade …` | **Queue live trade** → **Execute YES** |

## Interactive buttons

| Button | Action |
|--------|--------|
| Status / Preflight | Session + GO/NO-GO checklist |
| Go live | `./pmx go-live` |
| Scout / Trader mode | Switches Hermes skill set |
| Approve (brief) | Sets `approved: true` in frontmatter |
| Queue live trade | Preview + pending token (5 min) |
| Execute YES | Runs trade with Telegram one-time confirm |
| Cancel | Discards pending trade |

## Commands reference

```bash
./pmx telegram              # start bot
./pmx activate-live         # enable live trading session
./pmx activate-live --bot   # go-live + start bot
./scripts/telegram-bot.sh
```

Telegram slash commands: `/start` `/status` `/preflight` `/golive` `/scout` `/trader` `/briefs` `/scenarios`

## Safety

1. `TELEGRAM_ALLOWED_CHAT_IDS` — required allowlist
2. `./pmx go-live` — read-only off for session
3. Brief `approved: true` — Trader gate
4. Double confirm — Queue + Execute YES
5. One-time trade tokens — expire in 5 minutes
6. Audit log — same as terminal trades (`trade_safety_audit_log`)

Emergency: use terminal `./pmx stop on "reason"` or `./pmx panic` (PANIC confirm still in terminal for panic).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Unauthorized chat | Add your chat id to `TELEGRAM_ALLOWED_CHAT_IDS` |
| READ-ONLY blocked | `/golive` or `./pmx activate-live` |
| Hermes timeout | Shorter message; set `TELEGRAM_HERMES_TIMEOUT=180` |
| Trade expired | Tap Queue again within 5 minutes |
| Bot not installed | `pip install -r requirements-telegram.txt` |

See also: `docs/multi-agent.md` · `hermes/README.md` · `docs/commands.md`
