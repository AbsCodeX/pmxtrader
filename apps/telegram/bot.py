"""Telegram bot entrypoint — Hermes + ./pmx with interactive confirmations."""

from __future__ import annotations

import asyncio
import logging
import re
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.bridge.telegram_trade import chat_is_allowed, get_pending  # noqa: E402
from apps.telegram.briefs import approve_brief, brief_summary  # noqa: E402
from apps.telegram.cache import pop_value, store_value  # noqa: E402
from apps.telegram.config import TelegramConfig, load_config  # noqa: E402
from apps.telegram.hermes_bridge import ask_hermes, clear_session  # noqa: E402
from apps.telegram import keyboards  # noqa: E402
from apps.telegram import pmx_runner  # noqa: E402
from apps.telegram import templates  # noqa: E402
from apps.telegram.ui import (  # noqa: E402
    error_message,
    help_card,
    loading_message,
    main_menu_message,
    menu_keyboard,
    route_callback,
    trading_allowed_in_chat,
)
from apps.telegram.ui.router import loading_for_menu  # noqa: E402

log = logging.getLogger("pmxtrader.telegram")

URL_RE = re.compile(r"https?://[^\s<>]+", re.I)
PMX_CMD_RE = re.compile(r"(?m)^\./pmx[^\n`]+")


def _cfg(context: ContextTypes.DEFAULT_TYPE) -> TelegramConfig:
    return context.application.bot_data["cfg"]


async def _guard(update: Update) -> bool:
    chat = update.effective_chat
    if chat is None or not chat_is_allowed(chat.id):
        if update.effective_message:
            await update.effective_message.reply_text("Unauthorized chat.")
        return False
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    context.user_data["mode"] = "scout"
    await update.message.reply_text(  # type: ignore[union-attr]
        main_menu_message(),
        reply_markup=keyboards.main_menu(),
        parse_mode="Markdown",
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    await update.message.reply_text(  # type: ignore[union-attr]
        main_menu_message(),
        reply_markup=keyboards.main_menu(),
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    cfg = _cfg(context)
    await update.message.reply_text(pmx_runner.status_text(cfg))  # type: ignore[union-attr]


async def cmd_preflight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    cfg = _cfg(context)
    await update.message.reply_text(pmx_runner.preflight_text(cfg))  # type: ignore[union-attr]


async def cmd_golive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    cfg = _cfg(context)
    result = pmx_runner.go_live(cfg)
    text = result.stdout or result.stderr or ("Live enabled" if result.ok else "Go-live failed")
    await update.message.reply_text(text)  # type: ignore[union-attr]


async def cmd_scenarios(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    await update.message.reply_text(templates.scenario_help())  # type: ignore[union-attr]


async def cmd_briefs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    cfg = _cfg(context)
    await update.message.reply_text(  # type: ignore[union-attr]
        "Active briefs — tap Approve before Trader.",
        reply_markup=keyboards.briefs_keyboard(cfg),
    )


async def cmd_scout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Usage: /scout your research question")  # type: ignore[union-attr]
        return
    await _hermes_reply(update, context, query, mode="scout")


async def cmd_trader(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /trader briefs/active/YOUR-BRIEF.md")  # type: ignore[union-attr]
        return
    brief_rel = context.args[0]
    cfg = _cfg(context)
    brief_path = cfg.root / brief_rel
    if not brief_path.is_file():
        await update.message.reply_text(f"Brief not found: {brief_rel}")  # type: ignore[union-attr]
        return
    from apps.telegram.briefs import brief_is_approved

    if not brief_is_approved(brief_path):
        await update.message.reply_text("Brief not approved. Tap Approve in /briefs first.")  # type: ignore[union-attr]
        return
    extra = f"Approved brief:\n{brief_path.read_text(encoding='utf-8')[:6000]}"
    await _hermes_reply(update, context, "Prepare live trade commands from this brief.", mode="trader", extra=extra)


async def _hermes_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message: str,
    *,
    mode: str,
    extra: str = "",
) -> None:
    cfg = _cfg(context)
    chat = update.effective_chat
    msg = update.effective_message
    if chat is None or msg is None:
        return
    status = await msg.reply_text("Thinking…")
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: ask_hermes(cfg, message, mode=mode, extra_context=extra),
    )
    text = templates.hermes_reply(result["text"])
    await status.edit_text(text[:4096])
    for match in PMX_CMD_RE.finditer(result["text"]):
        cmd = match.group(0).strip()
        if any(x in cmd for x in (" trade ", " poly trade ", " poly sell ", " poly close ")):
            await msg.reply_text(
                templates.trade_preview("From Hermes", cmd),
                reply_markup=_queue_keyboard(cmd),
            )


async def _handle_ui_route(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    route,
) -> bool:
    """Handle pmx: UI callbacks. Returns True if handled."""
    query = update.callback_query
    if query is None or query.message is None:
        return True
    cfg = _cfg(context)
    chat = update.effective_chat
    chat_type = chat.type if chat else "private"

    if route.kind == "noop":
        return True

    if route.blocked_in_group and not trading_allowed_in_chat(query.message.chat_id, chat_type):
        await query.message.reply_text(
            error_message(
                "Trading blocked",
                "Live trading is private-chat only. Set PMX_TELEGRAM_GROUP_TRADING=1 to allow groups.",
            )
        )
        return True

    if route.kind == "show_menu":
        title = "Menu" if route.menu_id == "main" else route.menu_id.replace("_", " ").title()
        await query.message.reply_text(
            f"*{title}*\n\nTap a button or type a command.",
            reply_markup=menu_keyboard(route.menu_id),
            parse_mode="Markdown",
        )
        return True

    if route.kind == "help":
        await query.message.reply_text(help_card(), parse_mode="Markdown")
        return True

    if route.kind == "set_mode":
        if route.sub_action in ("ai", "scout"):
            context.user_data["mode"] = "scout"
            label = "AI (Scout)"
        elif route.sub_action in ("manual", "trader"):
            context.user_data["mode"] = "trader"
            label = "Manual (Trader)"
        else:
            current = context.user_data.get("mode", "scout")
            context.user_data["mode"] = "trader" if current == "scout" else "scout"
            label = context.user_data["mode"]
        await query.message.reply_text(f"Trading mode: {label}")
        return True

    if route.kind == "hermes_prompt":
        await query.message.reply_text(route.prompt or "Ask Hermes anything.")
        return True

    if route.kind == "refresh":
        await query.message.reply_text(loading_for_menu(route.menu_id))
        if route.menu_id == "portfolio":
            await query.message.reply_text(pmx_runner.status_text(cfg))
        elif route.menu_id == "settings":
            await query.message.reply_text(pmx_runner.preflight_text(cfg))
        else:
            await query.message.reply_text(
                f"Refreshed {route.menu_id}.",
                reply_markup=menu_keyboard(route.menu_id),
            )
        return True

    if route.kind == "quick":
        prompts = {
            "analyze": "Paste a market URL or name to analyze.",
            "watch": "Which market should I watch?",
            "trade": "Approved brief required — use /briefs then /trader.",
            "alert": "Describe the alert condition.",
        }
        text = prompts.get(route.sub_action, "How can I help?")
        if route.sub_action in ("analyze", "watch", "alert"):
            await _hermes_reply(update, context, text, mode=context.user_data.get("mode", "scout"))
        else:
            await query.message.reply_text(text)
        return True

    if route.kind == "action":
        await query.message.reply_text(loading_message(route.sub_action or route.menu_id))
        if route.menu_id == "portfolio" and route.sub_action == "positions":
            await query.message.reply_text(pmx_runner.status_text(cfg))
        elif route.menu_id == "settings" and route.sub_action == "api":
            await query.message.reply_text(pmx_runner.preflight_text(cfg))
        elif route.menu_id == "agents" and route.sub_action == "logs":
            from apps.telegram.ui import agent_logs_table

            await query.message.reply_text(
                agent_logs_table(
                    [{"time": "—", "agent": "—", "action": "—", "detail": "No logs yet"}]
                ),
                parse_mode="Markdown",
            )
        else:
            await query.message.reply_text(
                f"{route.menu_id}/{route.sub_action} — ask Hermes for details.",
                reply_markup=menu_keyboard(route.menu_id),
            )
        return True

    if route.kind == "trade_confirm":
        pending = get_pending(route.token)
        if not pending:
            await query.message.reply_text("Trade expired — queue again.")
            return True
        await query.message.reply_text("Executing…")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, lambda: pmx_runner.execute_pending_trade(cfg, pending)
        )
        await query.message.reply_text(
            templates.trade_result(result.ok, result.stdout, result.stderr)
        )
        return True

    if route.kind == "trade_cancel":
        from apps.bridge.telegram_trade import discard_pending

        discard_pending(route.token)
        await query.message.reply_text("Trade cancelled.")
        return True

    return False


def _queue_keyboard(command: str):
    token = store_value("trade_cmd", command)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Queue live trade", callback_data=f"queue:{token}")]]
    )


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    msg = update.effective_message
    if msg is None or not msg.text:
        return
    text = msg.text.strip()
    cfg = _cfg(context)
    mode = context.user_data.get("mode", "scout")

    urls = URL_RE.findall(text)
    if urls and len(text.split()) <= 3:
        url = urls[0].rstrip(").,")
        context.user_data["last_url"] = url
        await msg.reply_text(templates.link_detected(url), reply_markup=keyboards.link_actions(url))
        await _hermes_reply(update, context, f"Research this market URL and suggest next steps: {url}", mode="scout")
        return

    lower = text.lower()
    if lower.startswith("quote "):
        args = text.split()[1:]
        result = pmx_runner.run_pmx(cfg, ["quote", *args])
        await msg.reply_text(result.stdout or result.stderr or "No output")
        return
    if lower.startswith("poly quote ") or lower.startswith("poly "):
        parts = text.split()
        result = pmx_runner.run_pmx(cfg, parts)
        await msg.reply_text(result.stdout or result.stderr or "No output")
        return
    if lower in ("status", "session"):
        await msg.reply_text(pmx_runner.status_text(cfg))
        return

    await _hermes_reply(update, context, text, mode=mode)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    query = update.callback_query
    if query is None or not query.data:
        return
    await query.answer()
    cfg = _cfg(context)
    chat_id = query.message.chat_id if query.message else 0
    data = query.data

    if data == "act:noop":
        return
    if data == "pmx:noop":
        return

    ui_route = route_callback(data)
    if ui_route is not None and ui_route.kind != "unknown":
        handled = await _handle_ui_route(update, context, ui_route)
        if handled:
            return

    if data == "act:menu":
        await query.message.reply_text(  # type: ignore[union-attr]
            main_menu_message(),
            reply_markup=keyboards.main_menu(),
            parse_mode="Markdown",
        )
        return
    if data == "act:status":
        await query.message.reply_text(pmx_runner.status_text(cfg))  # type: ignore[union-attr]
        return
    if data == "act:preflight":
        await query.message.reply_text(pmx_runner.preflight_text(cfg))  # type: ignore[union-attr]
        return
    if data == "act:golive":
        result = pmx_runner.go_live(cfg)
        await query.message.reply_text(result.stdout or result.stderr or "Done")  # type: ignore[union-attr]
        return
    if data == "act:scenarios":
        await query.message.reply_text(templates.scenario_help())  # type: ignore[union-attr]
        return
    if data == "act:clear":
        clear_session()
        await query.message.reply_text("Hermes session cleared.")  # type: ignore[union-attr]
        return
    if data == "act:briefs":
        await query.message.reply_text(  # type: ignore[union-attr]
            "Active briefs",
            reply_markup=keyboards.briefs_keyboard(cfg),
        )
        return
    if data.startswith("mode:"):
        context.user_data["mode"] = data.split(":", 1)[1]
        await query.message.reply_text(f"Mode: {context.user_data['mode']}")  # type: ignore[union-attr]
        return

    if data.startswith("brief:show:"):
        name = data.split(":", 2)[2]
        path = cfg.root / "briefs" / "active" / name
        await query.message.reply_text(brief_summary(path))  # type: ignore[union-attr]
        return
    if data.startswith("brief:approve:"):
        name = data.split(":", 2)[2]
        path = cfg.root / "briefs" / "active" / name
        ok, detail = approve_brief(path)
        await query.message.reply_text(f"{'OK' if ok else 'Fail'}: {detail}")  # type: ignore[union-attr]
        return

    if data == "link:scout":
        url = context.user_data.get("last_url", "")
        if url:
            await _hermes_reply(update, context, f"Deep scout on: {url}", mode="scout")
        return
    if data == "link:kalshi":
        url = context.user_data.get("last_url", "")
        if url:
            result = pmx_runner.run_pmx(cfg, ["link", url, "YES", "1"])
            await query.message.reply_text(result.stdout or result.stderr or "Done")  # type: ignore[union-attr]
        return
    if data == "link:poly":
        url = context.user_data.get("last_url", "")
        if url:
            result = pmx_runner.run_pmx(cfg, ["poly", "link", url, "long"])
            await query.message.reply_text(result.stdout or result.stderr or "Done")  # type: ignore[union-attr]
        return

    if data.startswith("queue:"):
        token = data.split(":", 1)[1]
        cmd = pop_value(token, kind="trade_cmd")
        if not cmd:
            await query.message.reply_text("Trade command expired — ask Hermes again.")  # type: ignore[union-attr]
            return
        pending, preview = pmx_runner.queue_trade_from_command(cfg, chat_id=chat_id, command_line=cmd)
        if pending is None:
            await query.message.reply_text(preview)  # type: ignore[union-attr]
            return
        await query.message.reply_text(  # type: ignore[union-attr]
            templates.trade_preview(preview, cmd),
            reply_markup=keyboards.trade_confirm(pending.token),
        )
        return

    if data.startswith("trade:preview:"):
        token = data.split(":", 2)[2]
        pending = get_pending(token)
        if not pending:
            await query.message.reply_text("Preview expired.")  # type: ignore[union-attr]
            return
        await query.message.reply_text(pending.preview[:4000])  # type: ignore[union-attr]
        return
    if data.startswith("trade:cancel:"):
        token = data.split(":", 2)[2]
        from apps.bridge.telegram_trade import discard_pending

        discard_pending(token)
        await query.message.reply_text("Trade cancelled.")  # type: ignore[union-attr]
        return
    if data.startswith("trade:exec:"):
        token = data.split(":", 2)[2]
        pending = get_pending(token)
        if not pending:
            await query.message.reply_text("Trade expired — queue again.")  # type: ignore[union-attr]
            return
        await query.message.reply_text("Executing…")  # type: ignore[union-attr]
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: pmx_runner.execute_pending_trade(cfg, pending))
        await query.message.reply_text(  # type: ignore[union-attr]
            templates.trade_result(result.ok, result.stdout, result.stderr)
        )
        return


def build_app(cfg: TelegramConfig) -> Application:
    app = Application.builder().token(cfg.bot_token).build()
    app.bot_data["cfg"] = cfg
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("preflight", cmd_preflight))
    app.add_handler(CommandHandler("golive", cmd_golive))
    app.add_handler(CommandHandler("scenarios", cmd_scenarios))
    app.add_handler(CommandHandler("briefs", cmd_briefs))
    app.add_handler(CommandHandler("scout", cmd_scout))
    app.add_handler(CommandHandler("trader", cmd_trader))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cfg = load_config()
    app = build_app(cfg)
    log.info("pmxtrader Telegram bot starting (chats=%s)", ",".join(cfg.allowed_chat_ids))
    app.run_polling(poll_interval=cfg.poll_interval, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
