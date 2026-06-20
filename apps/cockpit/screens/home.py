"""
Trading dashboard — WTF modules, cointop watchlist, GoAccess stats + access log.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, RichLog, Static

from apps.cockpit.bridge.live import LiveSnapshot
from apps.cockpit.widgets.sparkline import bar_gauge, fmt_price_color
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
    """Primary dashboard — terminal modules, 8s live refresh."""

    DEFAULT_CSS = """
    HomePane {
        height: 1fr;
        padding: 0 1;
        background: #050608;
    }
    #dash-toolbar {
        height: 1;
        margin-bottom: 0;
        color: #b8c5d6;
    }
    #dash-top, #dash-bottom {
        height: 1fr;
        min-height: 8;
    }
    .module {
        border: solid #1a2332;
        background: #050608;
        height: 1fr;
        width: 1fr;
        min-height: 6;
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
        background: #0a0e14;
        color: #00d4ff;
        text-align: center;
    }
    #mod-markets-table {
        height: 1fr;
        min-height: 5;
        background: #050608;
    }
    #mod-positions-log, #mod-activity-log {
        height: 1fr;
        background: #050608;
    }
    #mod-balances-body, #mod-health-body {
        height: 1fr;
        padding: 0 1;
        color: #e2eaf2;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="dash-toolbar"):
            yield Static(
                "[#8b9cb5]pmxtrader[/] [#eef2f8]desk[/]",
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
        act.write("[dim]access log · timestamp · status · command[/dim]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "go-analyze": "analyze",
            "go-chat": "chat",
            "go-diag": "diagnostics",
        }
        if event.button.id == "go-refresh":
            self.app.action_refresh_all()
        elif event.button.id in mapping:
            self.app.action_tab(mapping[event.button.id])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row = table.get_row(event.row_key)
        if row and len(row) >= 2 and row[1]:
            slug = str(row[1])
            url = f"https://polymarket.us/market/{slug}"
            if hasattr(self.app, "open_analyze"):
                self.app.open_analyze(url, run=True)
            else:
                self.app.notify(f"./pmx poly link '{url}' long")

    def render_snap(self, snap: LiveSnapshot) -> None:
        self.query_one("#stats-bar", StatsBar).apply_snapshot(snap)

        ks = snap.kill_switch
        if ks == "ON":
            ks_c = "#ff4466"
        elif ks == "OFF":
            ks_c = "#00ff9c"
        else:
            ks_c = "#ffb000"

        self.query_one("#mod-balances-body", Static).update(
            f"[#00ff9c]KAL[/] [#eef2f8]${snap.kalshi_available or '?'}[/]"
            f" / ${snap.kalshi_total or '?'}  [{ks_c}]{ks}[/]\n"
            f"[#00d4ff]POL[/] [#eef2f8]${snap.poly_available or '?'}[/]"
            f" / ${snap.poly_total or '?'}"
        )

        health = "\n".join(snap.health_lines) if snap.health_lines else "[#8b9cb5]checking…[/]"
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
            title = str(m.get("title", ""))[:36]
            table.add_row(title, m.get("slug", ""), price, vol, hits)

        pos = self.query_one("#mod-positions-log", RichLog)
        pos.clear()
        pos.write(snap.positions_preview or "[#8b9cb5]No positions[/]")
