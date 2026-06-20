/**
 * Callback data naming for pmxtrader Telegram UI.
 * Prefix `pmx:` keeps pmxtrader callbacks distinct from legacy `act:` / `trade:` handlers.
 */

export const CALLBACK_PREFIX = "pmx:" as const;
export const LEGACY_PREFIXES = ["act:", "trade:", "brief:", "link:", "queue:", "mode:"] as const;

export type CallbackAction =
  | "menu"
  | "nav"
  | "refresh"
  | "toggle"
  | "quick"
  | "confirm"
  | "cancel"
  | "page"
  | "noop";

export interface ParsedCallback {
  raw: string;
  prefix: string;
  action: CallbackAction | string;
  parts: string[];
}

/** Build callback_data string (max 64 bytes — keep segments short). */
export function buildCallback(action: string, ...parts: string[]): string {
  const body = [action, ...parts].filter(Boolean).join(":");
  const data = `${CALLBACK_PREFIX}${body}`;
  if (data.length > 64) {
    throw new Error(`callback_data too long (${data.length}): ${data}`);
  }
  return data;
}

export function parseCallback(data: string): ParsedCallback {
  if (data.startsWith(CALLBACK_PREFIX)) {
    const rest = data.slice(CALLBACK_PREFIX.length);
    const parts = rest.split(":");
    return {
      raw: data,
      prefix: CALLBACK_PREFIX,
      action: parts[0] ?? "",
      parts: parts.slice(1),
    };
  }
  const legacy = LEGACY_PREFIXES.find((p) => data.startsWith(p));
  return {
    raw: data,
    prefix: legacy ?? "",
    action: legacy ? legacy.replace(":", "") : "unknown",
    parts: data.split(":").slice(1),
  };
}

export const QUICK_ACTIONS = ["analyze", "watch", "trade", "alert"] as const;
export type QuickAction = (typeof QUICK_ACTIONS)[number];
