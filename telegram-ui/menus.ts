/**
 * Nested menu tree for pmxtrader Telegram UI.
 */

import { buildCallback } from "./callbacks.js";

export interface MenuItem {
  id: string;
  label: string;
  callback: string;
  description?: string;
  parent?: string;
}

export interface MenuSection {
  id: string;
  title: string;
  items: MenuItem[];
}

export const MAIN_MENU_ID = "main";

export const mainMenuItems: MenuItem[] = [
  { id: "ask", label: "Ask Hermes", callback: buildCallback("menu", "ask"), description: "Free-form chat with Hermes" },
  { id: "research", label: "Market Research", callback: buildCallback("menu", "research"), description: "Scout lane — compare, briefs" },
  { id: "markets", label: "Prediction Markets", callback: buildCallback("menu", "markets"), description: "Quotes, trending, watchlist" },
  { id: "portfolio", label: "Portfolio", callback: buildCallback("menu", "portfolio"), description: "Balances and positions" },
  { id: "trading_mode", label: "Trading Mode", callback: buildCallback("menu", "trading_mode"), description: "AI vs manual execution" },
  { id: "agents", label: "Agent Tools", callback: buildCallback("menu", "agents"), description: "Scout/Trader, logs, alerts" },
  { id: "settings", label: "Settings", callback: buildCallback("menu", "settings"), description: "Wallet, API, permissions" },
  { id: "help", label: "Help", callback: buildCallback("menu", "help"), description: "Commands and safety" },
];

export const subMenus: Record<string, MenuSection> = {
  markets: {
    id: "markets",
    title: "Prediction Markets",
    items: [
      { id: "trending", label: "Trending", callback: buildCallback("menu", "markets", "trending"), parent: "markets" },
      { id: "search", label: "Search", callback: buildCallback("menu", "markets", "search"), parent: "markets" },
      { id: "watchlist", label: "Watchlist", callback: buildCallback("menu", "markets", "watchlist"), parent: "markets" },
      { id: "back", label: "Back", callback: buildCallback("nav", "back", MAIN_MENU_ID), parent: "markets" },
    ],
  },
  portfolio: {
    id: "portfolio",
    title: "Portfolio",
    items: [
      { id: "positions", label: "Positions", callback: buildCallback("menu", "portfolio", "positions"), parent: "portfolio" },
      { id: "history", label: "History", callback: buildCallback("menu", "portfolio", "history"), parent: "portfolio" },
      { id: "risk", label: "Risk", callback: buildCallback("menu", "portfolio", "risk"), parent: "portfolio" },
      { id: "back", label: "Back", callback: buildCallback("nav", "back", MAIN_MENU_ID), parent: "portfolio" },
    ],
  },
  agents: {
    id: "agents",
    title: "Agent Tools",
    items: [
      { id: "mode", label: "AI / Manual", callback: buildCallback("toggle", "mode"), parent: "agents" },
      { id: "logs", label: "Logs", callback: buildCallback("menu", "agents", "logs"), parent: "agents" },
      { id: "alerts", label: "Alerts", callback: buildCallback("menu", "alerts"), parent: "agents" },
      { id: "agent_settings", label: "Settings", callback: buildCallback("menu", "agents", "settings"), parent: "agents" },
      { id: "back", label: "Back", callback: buildCallback("nav", "back", MAIN_MENU_ID), parent: "agents" },
    ],
  },
  alerts: {
    id: "alerts",
    title: "Alerts",
    items: [
      { id: "create", label: "Create", callback: buildCallback("menu", "alerts", "create"), parent: "alerts" },
      { id: "my", label: "My Alerts", callback: buildCallback("menu", "alerts", "my"), parent: "alerts" },
      { id: "back", label: "Back", callback: buildCallback("nav", "back", "agents"), parent: "alerts" },
    ],
  },
  settings: {
    id: "settings",
    title: "Settings",
    items: [
      { id: "wallet", label: "Wallet", callback: buildCallback("menu", "settings", "wallet"), parent: "settings" },
      { id: "api", label: "API Status", callback: buildCallback("menu", "settings", "api"), parent: "settings" },
      { id: "permissions", label: "Permissions", callback: buildCallback("menu", "settings", "permissions"), parent: "settings" },
      { id: "back", label: "Back", callback: buildCallback("nav", "back", MAIN_MENU_ID), parent: "settings" },
    ],
  },
  trading_mode: {
    id: "trading_mode",
    title: "Trading Mode",
    items: [
      { id: "ai", label: "AI Mode", callback: buildCallback("toggle", "mode", "ai"), parent: "trading_mode" },
      { id: "manual", label: "Manual Mode", callback: buildCallback("toggle", "mode", "manual"), parent: "trading_mode" },
      { id: "back", label: "Back", callback: buildCallback("nav", "back", MAIN_MENU_ID), parent: "trading_mode" },
    ],
  },
};

export function menuTitle(menuId: string): string {
  if (menuId === MAIN_MENU_ID) return "pmxtrader";
  return subMenus[menuId]?.title ?? menuId;
}

export function menuItemsFor(menuId: string): MenuItem[] {
  if (menuId === MAIN_MENU_ID) return mainMenuItems;
  return subMenus[menuId]?.items ?? mainMenuItems;
}
