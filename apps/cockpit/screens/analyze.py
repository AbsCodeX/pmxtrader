from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Select, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge import pmx
from apps.cockpit.widgets.output_log import OutputLog


class AnalyzePane(Vertical):
    DEFAULT_CSS = """
    AnalyzePane { padding: 1; height: 1fr; }
    #analyze-url { width: 1fr; }
    .row { height: auto; margin-bottom: 1; }
    #analyze-log { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Link analyzer[/bold]  [dim]Kalshi or Polymarket US[/dim]", markup=True)
        with Horizontal(classes="row"):
            yield Input(
                placeholder="https://kalshi.com/… or https://polymarket.us/market/…",
                id="analyze-url",
            )
        with Horizontal(classes="row"):
            yield Input(value="USA", placeholder="Kalshi outcome", id="analyze-outcome")
            yield Select(
                [("long", "long (yes)"), ("short", "short (no)")],
                id="analyze-side",
                prompt="Side",
            )
            yield Input(value="1", placeholder="size", id="analyze-size")
            yield Button("Analyze", variant="primary", id="analyze-run")
        yield OutputLog(id="analyze-log", markup=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "analyze-run":
            self.run_analysis()

    def on_input_submitted(self, event) -> None:
        if event.input.id == "analyze-url":
            self.run_analysis()

    def run_analysis(self) -> None:
        url = self.query_one("#analyze-url", Input).value.strip()
        if not url:
            self.app.notify("Paste a URL", severity="warning")
            return
        outcome = self.query_one("#analyze-outcome", Input).value.strip() or "USA"
        side = str(self.query_one("#analyze-side", Select).value or "long")
        size = float(self.query_one("#analyze-size", Input).value.strip() or "1")
        log = self.query_one("#analyze-log", OutputLog)
        log.clear()
        log.write("[dim]Analyzing (up to 30s)…[/dim]")
        self.run_worker(
            lambda: pmx.analyze_link(url, outcome, side, size),
            thread=True,
            exclusive=True,
            group="analyze",
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "analyze":
            return
        if event.state == WorkerState.ERROR:
            self.query_one("#analyze-log", OutputLog).write("[red]Analysis failed[/red]")
            return
        if event.state != WorkerState.SUCCESS:
            return
        r = event.worker.result
        body = r.get("stdout") or r.get("stderr") or r.get("error") or "No output"
        log = self.query_one("#analyze-log", OutputLog)
        log.clear()
        log.write_block(f"[{r.get('venue', '?')}] {r.get('url', '')}", body)
        if hasattr(self.app, "log_activity"):
            self.app.log_activity("analyze", body[:400])
