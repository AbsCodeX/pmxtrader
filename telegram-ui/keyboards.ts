/**
 * Inline keyboard builders (Telegram Bot API shape).
 * Python adapter mirrors this using ui-spec.json at runtime.
 */

import { buildCallback, QUICK_ACTIONS } from "./callbacks.js";
import { mainMenuItems, menuItemsFor, MAIN_MENU_ID } from "./menus.js";
import { loadMiniAppUrls, MINIAPP_LABELS } from "./miniapps.js";

export type ButtonKind = "callback" | "url" | "web_app";

export interface InlineButton {
  text: string;
  kind: ButtonKind;
  callback_data?: string;
  url?: string;
}

export interface InlineKeyboard {
  rows: InlineButton[][];
}

function chunk<T>(items: T[], size: number): T[][] {
  const rows: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    rows.push(items.slice(i, i + size));
  }
  return rows;
}

export function menuKeyboard(menuId: string = MAIN_MENU_ID): InlineKeyboard {
  const items = menuItemsFor(menuId);
  const buttons: InlineButton[] = items.map((item) => ({
    text: item.label,
    kind: "callback" as const,
    callback_data: item.callback,
  }));
  return { rows: chunk(buttons, 2) };
}

export function mainMenuKeyboard(): InlineKeyboard {
  return menuKeyboard(MAIN_MENU_ID);
}

export function backRefreshRow(menuId: string): InlineKeyboard {
  return {
    rows: [
      [
        { text: "Back", kind: "callback", callback_data: buildCallback("nav", "back", MAIN_MENU_ID) },
        { text: "Refresh", kind: "callback", callback_data: buildCallback("refresh", menuId) },
      ],
    ],
  };
}

export function paginationRow(menuId: string, page: number, totalPages: number): InlineKeyboard {
  const row: InlineButton[] = [];
  if (page > 0) {
    row.push({
      text: "Prev",
      kind: "callback",
      callback_data: buildCallback("page", menuId, "prev", String(page - 1)),
    });
  }
  row.push({ text: `${page + 1}/${totalPages}`, kind: "callback", callback_data: buildCallback("noop") });
  if page < totalPages - 1) {
    row.push({
      text: "Next",
      kind: "callback",
      callback_data: buildCallback("page", menuId, "next", String(page + 1)),
    });
  }
  return { rows: [row] };
}

export function confirmCancelRow(confirmCallback: string, cancelCallback: string): InlineKeyboard {
  return {
    rows: [
      [
        { text: "Confirm", kind: "callback", callback_data: confirmCallback },
        { text: "Cancel", kind: "callback", callback_data: cancelCallback },
      ],
    ],
  };
}

export function tradeConfirmKeyboard(token: string): InlineKeyboard {
  return {
    rows: [
      [{ text: "Review preview", kind: "callback", callback_data: `trade:preview:${token}` }],
      [
        { text: "Confirm execute", kind: "callback", callback_data: buildCallback("confirm", "trade", token) },
        { text: "Cancel", kind: "callback", callback_data: buildCallback("cancel", "trade", token) },
      ],
    ],
  };
}

export function quickActionsRow(): InlineKeyboard {
  return {
    rows: [
      QUICK_ACTIONS.map((action) => ({
        text: action.charAt(0).toUpperCase() + action.slice(1),
        kind: "callback" as const,
        callback_data: buildCallback("quick", action),
      })),
    ],
  };
}

export function miniAppRow(env: Record<string, string | undefined>): InlineKeyboard {
  const urls = loadMiniAppUrls(env);
  const keys = Object.keys(MINIAPP_LABELS) as (keyof typeof MINIAPP_LABELS)[];
  const buttons: InlineButton[] = keys.map((key) => ({
    text: MINIAPP_LABELS[key],
    kind: "web_app" as const,
    url: urls[key],
  }));
  return { rows: chunk(buttons, 2) };
}

export function legacyMainMenuBridge(): InlineKeyboard {
  return {
    rows: mainMenuItems.slice(0, 4).map((item) => [
      { text: item.label, kind: "callback", callback_data: item.callback },
    ]),
  };
}
