from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge import diagnostics as diag


class DiagnosticsPane(Vertical):
    DEFAULT_CSS = """
    DiagnosticsPane { padding: 1 0; }
    #diag-table { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]System diagnostics[/bold] — sidecar, keys, providers, Hermes")
        yield Button("Run all checks", id="diag-run", variant="primary")
        yield DataTable(id="diag-table", zebra_stripes=True)
        yield Static("", id="diag-summary")

    def on_mount(self) -> None:
        table = self.query_one("#diag-table", DataTable)
        table.add_columns("Check", "Status", "Detail")
        self.run_checks()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "diag-run":
            self.run_checks()

    def run_checks(self) -> None:
        self.query_one("#diag-summary", Static).update("[dim]Running…[/dim]")
        self.run_worker(lambda: diag.run_all(), thread=True, exclusive=True, group="diag")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "diag" or event.state != WorkerState.SUCCESS:
            return
        checks = event.worker.result
        table = self.query_one("#diag-table", DataTable)
        table.clear()
        ok_count = sum(1 for c in checks if c.ok)
        for c in checks:
            status = "[green]PASS[/green]" if c.ok else "[red]FAIL[/red]"
            table.add_row(c.name, status, c.detail)
        color = "green" if ok_count == len(checks) else "yellow"
        self.query_one("#diag-summary", Static).update(
            f"[{color}]{ok_count}/{len(checks)} checks passed[/]"
        )
