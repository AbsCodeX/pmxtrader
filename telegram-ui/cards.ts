/**
 * Card-style Telegram messages (Markdown).
 */

export interface MarketCardData {
  title: string;
  venue: string;
  outcome: string;
  price: string;
  volume?: string;
  url?: string;
  updatedAt?: string;
}

export interface TradeConfirmCardData {
  venue: string;
  market: string;
  outcome: string;
  side: string;
  size: string;
  estCost: string;
  command: string;
}

export interface AgentStatusCardData {
  mode: string;
  provider: string;
  sessionId?: string;
  killSwitch: string;
  readOnly: string;
  lastAction?: string;
}

export interface AlertCardData {
  title: string;
  condition: string;
  market: string;
  status: string;
  triggeredAt?: string;
}

export interface PortfolioCardData {
  kalshiBalance: string;
  polyBalance: string;
  openPositions: number;
  dayPnl?: string;
  riskNote?: string;
}

function bold(text: string): string {
  return `*${text}*`;
}

export function marketCard(data: MarketCardData): string {
  const lines = [
    bold("Market"),
    data.title,
    `Venue: ${data.venue}`,
    `Outcome: ${data.outcome}`,
    `Price: ${data.price}`,
  ];
  if (data.volume) lines.push(`Volume: ${data.volume}`);
  if (data.updatedAt) lines.push(`Updated: ${data.updatedAt}`);
  if (data.url) lines.push(`\n${data.url}`);
  return lines.join("\n");
}

export function tradeConfirmCard(data: TradeConfirmCardData): string {
  return [
    bold("Trade confirmation"),
    `Venue: ${data.venue}`,
    `Market: ${data.market}`,
    `Outcome: ${data.outcome}`,
    `Side: ${data.side} · Size: ${data.size}`,
    `Est. cost: ${data.estCost}`,
    "",
    bold("Command"),
    `\`${data.command}\``,
    "",
    "Tap Confirm — never executes from a single button alone.",
  ].join("\n");
}

export function agentStatusCard(data: AgentStatusCardData): string {
  const lines = [
    bold("Agent status"),
    `Mode: ${data.mode}`,
    `Provider: ${data.provider}`,
    `Kill switch: ${data.killSwitch}`,
    `Read-only: ${data.readOnly}`,
  ];
  if (data.sessionId) lines.push(`Session: ${data.sessionId.slice(0, 8)}…`);
  if (data.lastAction) lines.push(`Last: ${data.lastAction}`);
  return lines.join("\n");
}

export function alertCard(data: AlertCardData): string {
  const lines = [
    bold("Alert"),
    data.title,
    `Condition: ${data.condition}`,
    `Market: ${data.market}`,
    `Status: ${data.status}`,
  ];
  if (data.triggeredAt) lines.push(`Triggered: ${data.triggeredAt}`);
  return lines.join("\n");
}

export function portfolioCard(data: PortfolioCardData): string {
  const lines = [
    bold("Portfolio"),
    `Kalshi: ${data.kalshiBalance}`,
    `Polymarket US: ${data.polyBalance}`,
    `Open positions: ${data.openPositions}`,
  ];
  if (data.dayPnl) lines.push(`Day P&L: ${data.dayPnl}`);
  if (data.riskNote) lines.push(`\n${data.riskNote}`);
  return lines.join("\n");
}

export function loadingMessage(context: string): string {
  return `Checking ${context}…`;
}

export function errorMessage(context: string, detail: string): string {
  return `${bold("Error")} — ${context}\n\n${detail}`;
}

export function helpCard(): string {
  return [
    bold("pmxtrader help"),
    "Paste a Kalshi or Polymarket URL for Scout research.",
    "Use /menu anytime for inline buttons.",
    "",
    "Safety:",
    "• Live trades need Confirm + Execute (two taps)",
    "• Briefs need approved: true before Trader",
    "• ./pmx activate-live before real orders",
  ].join("\n");
}
