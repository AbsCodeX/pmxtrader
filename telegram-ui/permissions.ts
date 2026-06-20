/**
 * Permission helpers for Telegram UI (env-driven; mirrored in Python adapter).
 */

export interface PermissionConfig {
  allowedChatIds: string[];
  adminChatIds: string[];
  groupTradingEnabled: boolean;
}

export function loadPermissionConfig(env: Record<string, string | undefined>): PermissionConfig {
  const allowed = (env.TELEGRAM_ALLOWED_CHAT_IDS ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const adminRaw = env.TELEGRAM_ADMIN_CHAT_IDS ?? env.TELEGRAM_ALLOWED_CHAT_IDS ?? "";
  const adminChatIds = adminRaw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const groupTradingEnabled =
    (env.PMX_TELEGRAM_GROUP_TRADING ?? "0").trim() === "1";

  return { allowedChatIds: allowed, adminChatIds, groupTradingEnabled };
}

export function chatIsAllowed(chatId: string | number, cfg: PermissionConfig): boolean {
  if (!cfg.allowedChatIds.length) return false;
  return cfg.allowedChatIds.includes(String(chatId));
}

export function chatIsAdmin(chatId: string | number, cfg: PermissionConfig): boolean {
  return cfg.adminChatIds.includes(String(chatId));
}

/** Trading actions require private chat unless group trading flag is set. */
export function tradingAllowedInChat(
  chatId: string | number,
  chatType: string,
  cfg: PermissionConfig,
): boolean {
  if (!chatIsAllowed(chatId, cfg)) return false;
  if (chatType === "private") return true;
  return cfg.groupTradingEnabled;
}
