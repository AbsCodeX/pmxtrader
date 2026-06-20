"""Top ticker strip — compact terminal status bar."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Static

from apps.cockpit.bridge.live import LiveSnapshot


class TickerBar(Horizontal):
    DEFAULT_CSS = """
    TickerBar {
        height: 1;
        background: #0a0e14;
        color: #e2eaf2;
        padding: 0 1;
        content-align: left middle;
        border-bottom: solid #1a2332;
    }
    .tick {
        width: auto;
        padding: 0 1;
    }
    """

    kill = reactive("?")
    read_only = reactive(True)
    max_size = reactive("10")
    kalshi = reactive("—")
    poly = reactive("—")
    sidecar = reactive("…")

    def compose(self) -> ComposeResult:
        yield Static("▸PMX", classes="tick")
        yield Static("", id="t-kill", classes="tick", markup=True)
        yield Static("", id="t-ro", classes="tick", markup=True)
        yield Static("", id="t-max", classes="tick")
        yield Static("", id="t-kalshi", classes="tick", markup=True)
        yield Static("", id="t-poly", classes="tick", markup=True)
        yield Static("", id="t-side", classes="tick", markup=True)
        yield Static("", id="t-clock", classes="tick")

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick_clock)

    def _tick_clock(self) -> None:
        self.query_one("#t-clock", Static).update(datetime.now().strftime(" %H:%M:%S "))

    def apply_snapshot(self, snap: LiveSnapshot) -> None:
        self.kill = snap.kill_switch
        self.read_only = snap.read_only
        self.max_size = str(int(snap.max_trade_contracts or 10))
        self.kalshi = snap.kalshi_available or "?"
        self.poly = snap.poly_available or "?"
        self.sidecar = "UP" if snap.sidecar_ok else "DN"

    def watch_kill(self, v: str) -> None:
        color = "#ff4466" if v == "ON" else ("#00ff9c" if v == "OFF" else "#ffb000")
        self.query_one("#t-kill", Static).update(f" [{color}]KILL:{v}[/] ")

    def watch_read_only(self, v: bool) -> None:
        color = "#ffb000" if v else "#00ff9c"
        label = "RO" if v else "LIVE"
        self.query_one("#t-ro", Static).update(f" [{color}]{label}[/] ")

    def watch_max_size(self, v: str) -> None:
        self.query_one("#t-max", Static).update(f" MAX:{v} ")

    def watch_kalshi(self, v: str) -> None:
        self.query_one("#t-kalshi", Static).update(f" [#00ff9c]K${v}[/] ")

    def watch_poly(self, v: str) -> None:
        self.query_one("#t-poly", Static).update(f" [#00d4ff]P${v}[/] ")

    def watch_sidecar(self, v: str) -> None:
        color = "#00ff9c" if v == "UP" else "#ff4466"
        self.query_one("#t-side", Static).update(f" [{color}]CAR:{v}[/] ")
