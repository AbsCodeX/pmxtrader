from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge.live import fetch_positions_text
from apps.cockpit.widgets.output_log import OutputLog


class PositionsPane(Vertical):
    DEFAULT_CSS = """
    PositionsPane { padding: 1; height: 1fr; }
    #pos-log { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Positions & orders[/bold]  [dim]Kalshi + Poly US[/dim]", markup=True)
        yield Button("Reload", id="pos-refresh", variant="primary")
        yield OutputLog(id="pos-log", markup=True)

    def on_mount(self) -> None:
        self.reload_positions()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pos-refresh":
            self.reload_positions()

    def reload_positions(self) -> None:
        log = self.query_one("#pos-log", OutputLog)
        log.clear()
        log.write("[dim]Loading…[/dim]")
        self.run_worker(fetch_positions_text, thread=True, exclusive=True, group="positions")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "positions":
            return
        log = self.query_one("#pos-log", OutputLog)
        if event.state == WorkerState.ERROR:
            log.clear()
            log.write("[red]Failed to load positions[/red]")
            if event.worker.error:
                log.write_safe(str(event.worker.error))
            self.app.notify("Failed to load positions", severity="error")
            return
        if event.state != WorkerState.SUCCESS:
            return
        log.clear()
        log.write_safe(event.worker.result)
