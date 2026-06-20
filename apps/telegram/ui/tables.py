"""Monospace tables — mirrors telegram/tables.ts."""

from __future__ import annotations

MARKET_COLUMNS = [
    ("symbol", "Market", 14),
    ("outcome", "Out", 6),
    ("bid", "Bid", 6),
    ("ask", "Ask", 6),
    ("vol", "Vol", 8),
]

POSITION_COLUMNS = [
    ("venue", "Venue", 8),
    ("market", "Market", 14),
    ("side", "Side", 6),
    ("qty", "Qty", 5),
    ("avg", "Avg", 6),
]

AGENT_LOG_COLUMNS = [
    ("time", "Time", 8),
    ("agent", "Agent", 8),
    ("action", "Action", 10),
    ("detail", "Detail", 20),
]


def _pad(value: str, width: int) -> str:
    text = value if len(value) <= width else value[: width - 1] + "…"
    return text.ljust(width)


def format_table(
    columns: list[tuple[str, str, int]],
    rows: list[dict[str, str]],
    title: str = "",
) -> str:
    header = " ".join(_pad(hdr, width) for _, hdr, width in columns)
    divider = " ".join("-" * width for _, _, width in columns)
    body = [
        " ".join(_pad(str(row.get(key, "")), width) for key, _, width in columns)
        for row in rows
    ]
    table = "\n".join([header, divider, *body])
    prefix = f"*{title}*\n\n" if title else ""
    return f"{prefix}```\n{table}\n```"


def markets_table(rows: list[dict[str, str]]) -> str:
    return format_table(MARKET_COLUMNS, rows, "Markets")


def positions_table(rows: list[dict[str, str]]) -> str:
    return format_table(POSITION_COLUMNS, rows, "Positions")


def agent_logs_table(rows: list[dict[str, str]]) -> str:
    return format_table(AGENT_LOG_COLUMNS, rows, "Agent logs")
