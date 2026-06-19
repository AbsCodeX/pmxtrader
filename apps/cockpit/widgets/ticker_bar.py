"""Top ticker strip — inspired by ticker/cointop/mop live quote bars."""

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
        background: #1e293b;
        color: #e2e8f0;
        padding: 0 1;
        content-align: left middle;
    }
    .tick {
        width: auto;
        padding: 0 1;
    }
    .tick-label { color: #94a3b8; }
    .tick-val { text-style: bold; }
    .tick-warn { color: #fbbf24; }
    .tick-ok { color: #4ade80; }
    .tick-bad { color: #f87171; }
    .tick-cyan { color: #22d3ee; }
    .tick-clock { color: #a78bfa; margin-left: 1; }
    """

    kill = reactive("?")
    kalshi = reactive("—")
    poly = reactive("—")
    sidecar = reactive("…")
    updated = reactive("")

    def compose(self) -> ComposeResult:
        yield Static(" PMX ", classes="tick tick-cyan")
        yield Static("", id="t-kill", classes="tick")
        yield Static("", id="t-kalshi", classes="tick")
        yield Static("", id="t-poly", classes="tick")
        yield Static("", id="t-side", classes="tick")
        yield Static("", id="t-clock", classes="tick tick-clock")

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick_clock)

    def _tick_clock(self) -> None:
        self.query_one("#t-clock", Static).update(datetime.now().strftime(" %H:%M:%S "))

    def apply_snapshot(self, snap: LiveSnapshot) -> None:
        self.kill = snap.kill_switch
        self.kalshi = snap.kalshi_available or "?"
        self.poly = snap.poly_available or "?"
        self.sidecar = "LIVE" if snap.sidecar_ok else "DOWN"
        self.updated = datetime.now().strftime("%H:%M:%S")

    def watch_kill(self, v: str) -> None:
        cls = "tick tick-bad" if v == "ON" else "tick tick-ok"
        self.query_one("#t-kill", Static).set_classes(cls)
        self.query_one("#t-kill", Static).update(f" KILL:{v} ")

    def watch_kalshi(self, v: str) -> None:
        self.query_one("#t-kalshi", Static).update(f" KALSHI ${v} ")

    def watch_poly(self, v: str) -> None:
        self.query_one("#t-poly", Static).update(f" POLY ${v} ")

    def watch_sidecar(self, v: str) -> None:
        cls = "tick tick-ok" if v == "LIVE" else "tick tick-warn"
        self.query_one("#t-side", Static).set_classes(cls)
        self.query_one("#t-side", Static).update(f" SIDECAR:{v} ")
