/**
 * Monospace table formatters for Telegram (wrap in ``` fences).
 */

export interface TableColumn {
  key: string;
  header: string;
  width: number;
}

function pad(value: string, width: number): string {
  const text = value.length > width ? value.slice(0, width - 1) + "…" : value;
  return text.padEnd(width);
}

export function formatTable(
  columns: TableColumn[],
  rows: Record<string, string>[],
  title?: string,
): string {
  const header = columns.map((c) => pad(c.header, c.width)).join(" ");
  const divider = columns.map((c) => "-".repeat(c.width)).join(" ");
  const body = rows.map((row) =>
    columns.map((c) => pad(String(row[c.key] ?? ""), c.width)).join(" "),
  );
  const table = [header, divider, ...body].join("\n");
  const prefix = title ? `*${title}*\n\n` : "";
  return `${prefix}\`\`\`\n${table}\n\`\`\``;
}

export const MARKET_COLUMNS: TableColumn[] = [
  { key: "symbol", header: "Market", width: 14 },
  { key: "outcome", header: "Out", width: 6 },
  { key: "bid", header: "Bid", width: 6 },
  { key: "ask", header: "Ask", width: 6 },
  { key: "vol", header: "Vol", width: 8 },
];

export const POSITION_COLUMNS: TableColumn[] = [
  { key: "venue", header: "Venue", width: 8 },
  { key: "market", header: "Market", width: 14 },
  { key: "side", header: "Side", width: 6 },
  { key: "qty", header: "Qty", width: 5 },
  { key: "avg", header: "Avg", width: 6 },
];

export const AGENT_LOG_COLUMNS: TableColumn[] = [
  { key: "time", header: "Time", width: 8 },
  { key: "agent", header: "Agent", width: 8 },
  { key: "action", header: "Action", width: 10 },
  { key: "detail", header: "Detail", width: 20 },
];

export function marketsTable(rows: Record<string, string>[]): string {
  return formatTable(MARKET_COLUMNS, rows, "Markets");
}

export function positionsTable(rows: Record<string, string>[]): string {
  return formatTable(POSITION_COLUMNS, rows, "Positions");
}

export function agentLogsTable(rows: Record<string, string>[]): string {
  return formatTable(AGENT_LOG_COLUMNS, rows, "Agent logs");
}
