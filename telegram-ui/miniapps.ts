/**
 * Telegram Mini App (WebApp) button URLs — placeholders from env/config.
 */

export interface MiniAppUrls {
  dashboard: string;
  terminal: string;
  portfolio: string;
  research: string;
  agents: string;
  settings: string;
}

export const MINIAPP_ENV_KEYS = {
  dashboard: "PMX_TELEGRAM_MINIAPP_DASHBOARD",
  terminal: "PMX_TELEGRAM_MINIAPP_TERMINAL",
  portfolio: "PMX_TELEGRAM_MINIAPP_PORTFOLIO",
  research: "PMX_TELEGRAM_MINIAPP_RESEARCH",
  agents: "PMX_TELEGRAM_MINIAPP_AGENTS",
  settings: "PMX_TELEGRAM_MINIAPP_SETTINGS",
} as const;

export function loadMiniAppUrls(env: Record<string, string | undefined>): MiniAppUrls {
  return {
    dashboard: env.PMX_TELEGRAM_MINIAPP_DASHBOARD?.trim() || "https://example.com/pmx/dashboard",
    terminal: env.PMX_TELEGRAM_MINIAPP_TERMINAL?.trim() || "https://example.com/pmx/terminal",
    portfolio: env.PMX_TELEGRAM_MINIAPP_PORTFOLIO?.trim() || "https://example.com/pmx/portfolio",
    research: env.PMX_TELEGRAM_MINIAPP_RESEARCH?.trim() || "https://example.com/pmx/research",
    agents: env.PMX_TELEGRAM_MINIAPP_AGENTS?.trim() || "https://example.com/pmx/agents",
    settings: env.PMX_TELEGRAM_MINIAPP_SETTINGS?.trim() || "https://example.com/pmx/settings",
  };
}

export const MINIAPP_LABELS: Record<keyof MiniAppUrls, string> = {
  dashboard: "Open Dashboard",
  terminal: "Trading Terminal",
  portfolio: "Portfolio",
  research: "Research Board",
  agents: "Agent Control Center",
  settings: "Settings",
};
