from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static

from apps.cockpit.bridge import pmx
from apps.cockpit.widgets.output_log import OutputLog


class PositionsPane(Vertical):
    DEFAULT_CSS = """
    PositionsPane { padding: 1 0; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Open positions & orders[/bold]")
        yield Button("Refresh", id="pos-refresh", variant="primary")
        yield OutputLog(id="pos-log", markup=True)

    def on_mount(self) -> None:
        self.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pos-refresh":
            self.refresh()

    def refresh(self) -> None:
        log = self.query_one("#pos-log", OutputLog)
        log.clear()
        for title, args in (
            ("Kalshi positions", ("positions",)),
            ("Poly US positions", ("poly", "positions")),
            ("Poly US open orders", ("poly", "orders")),
        ):
            r = pmx.run_pmx(*args)
            log.write_block(title, r.get("stdout") or r.get("stderr") or "")
