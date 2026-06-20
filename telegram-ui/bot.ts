/**
 * pmxtrader Telegram bot UI layer — orchestration helpers.
 * Runtime for Hermes gateway: use clarify tool with menu labels from menus.ts.
 * Runtime for ./pmx telegram: Python adapter in apps/telegram/ui/.
 */

import { helpCard } from "./cards.js";
import { mainMenuKeyboard, menuKeyboard, quickActionsRow } from "./keyboards.js";
import { MAIN_MENU_ID, menuTitle } from "./menus.js";
import { loadPermissionConfig, tradingAllowedInChat } from "./permissions.js";

export const UI_VERSION = "1.0.0";

export interface BotUiContext {
  chatId: string;
  chatType: string;
  env: Record<string, string | undefined>;
}

export function mainMenuMessage(): string {
  return [
    "*pmxtrader*",
    "",
    "Choose a section below. Live trades always need Confirm — never one-tap execute.",
    "",
    helpCard().split("\n").slice(0, 3).join("\n"),
  ].join("\n");
}

export function menuScreen(menuId: string = MAIN_MENU_ID): { text: string; keyboard: ReturnType<typeof menuKeyboard> } {
  return {
    text: `*${menuTitle(menuId)}*\n\nTap a button or type a command.`,
    keyboard: menuKeyboard(menuId),
  };
}

export function canTradeInChat(ctx: BotUiContext): boolean {
  const perms = loadPermissionConfig(ctx.env);
  return tradingAllowedInChat(ctx.chatId, ctx.chatType, perms);
}

export { mainMenuKeyboard, quickActionsRow, menuKeyboard };
