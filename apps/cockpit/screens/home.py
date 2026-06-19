"""
Trading dashboard — WTF modules, cointop watchlist, GoAccess stats + access log.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, RichLog, Static

from apps.cockpit.bridge.live import LiveSnapshot
from apps.cockpit.widgets.sparkline import bar_gauge, fmt_price_color, sparkline
from apps.cockpit.widgets.stats_bar import StatsBar


def _safe_float(raw: str | None) -> float:
    try:
        return float(raw) if raw else 0.0
    except (TypeError, ValueError):
        return 0.0


def _vol_bar(volume: str, max_vol: float, width: int = 10) -> str:
    try:
        v = float(str(volume).replace(",", ""))
    except (TypeError, ValueError):
        return "░" * width
    return bar_gauge(v, max(max_vol, 1.0), width)


class HomePane(Vertical):
    """Primary dashboard — GoAccess summary + modular panels, 12s refresh."""

    DEFAULT_CSS = """
    HomePane {
        height: 1fr;
        padding: 0 1 1;
        background: #010409;
    }
    #dash-toolbar {
        height: auto;
        margin-bottom: 1;
        color: #c9d1d9;
    }
    #dash-top, #dash-bottom {
        height: 1fr;
        min-height: 10;
    }
    .module {
        border: solid #30363d;
        background: #0d1117;
        height: 1fr;
        width: 1fr;
        min-height: 8;
    }
    #mod-markets {
        width: 2fr;
    }
    #mod-activity {
        width: 2fr;
    }
    .mod-title {
        dock: top;
        height: 1;
        background: #161b22;
        color: #58a6ff;
        text-align: center;
        text-style: bold;
    }
    #mod-markets-table {
        height: 1fr;
        min-height: 6;
        background: #0d1117;
    }
    #mod-positions-log, #mod-activity-log {
        height: 1fr;
        background: #0d1117;
    }
    #mod-balances-body, #mod-health-body {
        height: 1fr;
        padding: 0 1;
        color: #c9d1d9;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="dash-toolbar"):
            yield Static(
                "[bold #58a6ff]pmxtrader[/]  [dim]GoAccess stats · WTF modules · cointop watchlist[/dim]",
                markup=True,
            )
            yield Button("↻", id="go-refresh", variant="primary")
            yield Button("Analyze", id="go-analyze")
            yield Button("AI", id="go-chat", variant="success")
            yield Button("Diag", id="go-diag")

        yield StatsBar(id="stats-bar")

        with Horizontal(id="dash-top"):
            with Vertical(classes="module", id="mod-balances"):
                yield Static(" BALANCES ", classes="mod-title")
                yield Static("Loading…", id="mod-balances-body", markup=True)

            with Vertical(classes="module", id="mod-health"):
                yield Static(" SYSTEM HEALTH ", classes="mod-title")
                yield Static("…", id="mod-health-body", markup=True)

            with Vertical(classes="module", id="mod-markets"):
                yield Static(" TOP MARKETS ", classes="mod-title")
                yield DataTable(id="mod-markets-table", zebra_stripes=True, cursor_type="row")

        with Horizontal(id="dash-bottom"):
            with Vertical(classes="module", id="mod-positions"):
                yield Static(" POSITIONS ", classes="mod-title")
                yield RichLog(id="mod-positions-log", markup=True, wrap=True)

            with Vertical(classes="module", id="mod-activity"):
                yield Static(" ACCESS LOG ", classes="mod-title")
                yield RichLog(id="mod-activity-log", markup=True, wrap=True)

    def on_mount(self) -> None:
        table = self.query_one("#mod-markets-table", DataTable)
        table.add_columns("Market", "Slug", "Price", "Vol", "Hits")
        act = self.query_one("#mod-activity-log", RichLog)
        act.write("[dim]GoAccess-style live log — timestamp · status · command[/dim]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "go-analyze": "analyze",
            "go-chat": "chat",
            "go-diag": "diagnostics",
        }
        if event.button.id == "go-refresh":
            self.app.poll_live()
        elif event.button.id in mapping:
            self.app.action_tab(mapping[event.button.id])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row = table.get_row(event.row_key)
        if row and len(row) >= 2 and row[1]:
            slug = str(row[1])
            msg = f"Selected: {slug}"
            if hasattr(self.app, "log_activity"):
                self.app.log_activity("poly quote", msg, ok=True)
            self.app.notify(f"./pmx poly quote {slug} long")

    def render_snap(self, snap: LiveSnapshot) -> None:
        self.query_one("#stats-bar", StatsBar).apply_snapshot(snap)

        ks = snap.kill_switch
        if ks == "ON":
            ks_c = "#f85149"
        elif ks == "OFF":
            ks_c = "#3fb950"
        else:
            ks_c = "#d29922"
        k_avail = _safe_float(snap.kalshi_available)
        p_avail = _safe_float(snap.poly_available)

        self.query_one("#mod-balances-body", Static).update(
            f"[bold #58a6ff]Kalshi[/]  [{ks_c}]kill {ks}[/]\n"
            f"  cash [#39c5cf]${snap.kalshi_available or '?'}[/]  "
            f"total ${snap.kalshi_total or '?'}\n"
            f"  {bar_gauge(k_avail, max(k_avail, 100))}\n"
            f"  [#8b949e]{sparkline(snap.spark_kalshi)}[/]\n\n"
            f"[bold #58a6ff]Poly US[/]\n"
            f"  cash [#39c5cf]${snap.poly_available or '?'}[/]  "
            f"total ${snap.poly_total or '?'}\n"
            f"  {bar_gauge(p_avail, max(p_avail, 500))}\n"
            f"  [#8b949e]{sparkline(snap.spark_poly)}[/]"
        )

        health = "\n".join(snap.health_lines) if snap.health_lines else "[dim]checking…[/dim]"
        self.query_one("#mod-health-body", Static).update(health)

        vols: list[float] = []
        for m in snap.markets:
            try:
                vols.append(float(str(m.get("volume", "0")).replace(",", "")))
            except (TypeError, ValueError):
                pass
        max_vol = max(vols) if vols else 1.0

        table = self.query_one("#mod-markets-table", DataTable)
        table.clear(columns=False)
        for m in snap.markets:
            price = fmt_price_color(str(m.get("price", "—")))
            vol = m.get("volume", "")
            hits = _vol_bar(str(vol), max_vol)
            table.add_row(m.get("title", ""), m.get("slug", ""), price, vol, hits)

        pos = self.query_one("#mod-positions-log", RichLog)
        pos.clear()
        pos.write(snap.positions_preview or "[dim]No positions[/dim]")
