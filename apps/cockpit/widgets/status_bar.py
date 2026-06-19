from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from apps.cockpit.bridge.live import LiveSnapshot


class LiveStatusBar(Horizontal):
    """Top strip — auto-updated balances and kill switch."""

    DEFAULT_CSS = """
    LiveStatusBar {
        height: 3;
        background: $panel;
        border: solid $primary;
        padding: 0 1;
        content-align: left middle;
    }
    .pill {
        width: auto;
        height: 1;
        padding: 0 1;
        margin-right: 1;
        background: $surface;
        border: solid $border;
    }
    .pill-warn { color: $warning; border: solid $warning; }
    .pill-ok { color: $success; border: solid $success; }
    """

    kill_switch = reactive("?")
    kalshi = reactive("—")
    poly = reactive("—")
    sidecar = reactive("…")

    def compose(self) -> ComposeResult:
        yield Static("", id="pill-kill", classes="pill")
        yield Static("", id="pill-kalshi", classes="pill")
        yield Static("", id="pill-poly", classes="pill")
        yield Static("", id="pill-sidecar", classes="pill")

    def apply_snapshot(self, snap: LiveSnapshot) -> None:
        self.kill_switch = snap.kill_switch
        self.kalshi = snap.kalshi_available or "?"
        self.poly = snap.poly_available or "?"
        self.sidecar = "live" if snap.sidecar_ok else "check"

    def watch_kill_switch(self, value: str) -> None:
        pill = self.query_one("#pill-kill", Static)
        cls = "pill pill-warn" if value == "ON" else "pill pill-ok"
        pill.set_classes(cls)
        pill.update(f"Kill: {value}")

    def watch_kalshi(self, value: str) -> None:
        self.query_one("#pill-kalshi", Static).update(f"Kalshi ${value}")

    def watch_poly(self, value: str) -> None:
        self.query_one("#pill-poly", Static).update(f"Poly ${value}")

    def watch_sidecar(self, value: str) -> None:
        self.query_one("#pill-sidecar", Static).update(f"Sidecar {value}")
