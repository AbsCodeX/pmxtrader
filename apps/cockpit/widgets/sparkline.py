"""ASCII sparklines (sampler-style mini charts)."""

from __future__ import annotations

_BLOCKS = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float], width: int = 24) -> str:
    if not values:
        return "─" * width
    tail = values[-width:]
    lo, hi = min(tail), max(tail)
    if lo == hi:
        return _BLOCKS[4] * len(tail)
    span = hi - lo
    out = []
    for v in tail:
        idx = int((v - lo) / span * (len(_BLOCKS) - 1))
        out.append(_BLOCKS[idx])
    return "".join(out)


def bar_gauge(value: float, max_value: float, width: int = 20) -> str:
    if max_value <= 0:
        return "░" * width
    filled = min(width, max(0, int(value / max_value * width)))
    return "█" * filled + "░" * (width - filled)


def fmt_price_color(price: str) -> str:
    try:
        p = float(price)
        if p >= 0.7:
            return f"[green]{price}[/green]"
        if p <= 0.3:
            return f"[red]{price}[/red]"
        return f"[yellow]{price}[/yellow]"
    except (TypeError, ValueError):
        return price or "—"
