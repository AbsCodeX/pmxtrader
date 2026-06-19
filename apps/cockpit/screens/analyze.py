from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Select, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge import pmx
from apps.cockpit.widgets.output_log import OutputLog


class AnalyzePane(Vertical):
    DEFAULT_CSS = """
    AnalyzePane { padding: 1 0; }
    #analyze-url { width: 1fr; }
    .row { height: auto; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Link analyzer[/bold] — Kalshi or Polymarket US URL")
        with Horizontal(classes="row"):
            yield Input(placeholder="https://kalshi.com/… or https://polymarket.us/market/…", id="analyze-url")
            yield Button("Paste", id="analyze-paste")
        with Horizontal(classes="row"):
            yield Input(value="USA", placeholder="Kalshi outcome", id="analyze-outcome")
            yield Select([("long", "long"), ("short", "short")], id="analyze-side", value="long")
            yield Input(value="1", placeholder="size", id="analyze-size")
            yield Button("Analyze", variant="primary", id="analyze-run")
            yield Button("Copy cmd", id="analyze-copy")
        yield OutputLog(id="analyze-log", markup=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "analyze-run":
            self._run()
        elif event.button.id == "analyze-paste":
            self.app.notify("Paste with Cmd+V in the URL field")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "analyze-url":
            self._run()

    def _run(self) -> None:
        url = self.query_one("#analyze-url", Input).value.strip()
        if not url:
            self.app.notify("Paste a URL first", severity="warning")
            return
        outcome = self.query_one("#analyze-outcome", Input).value.strip() or "USA"
        side = str(self.query_one("#analyze-side", Select).value or "long")
        size = self.query_one("#analyze-size", Input).value.strip() or "1"
        log = self.query_one("#analyze-log", OutputLog)
        log.clear()
        log.write("[dim]Analyzing…[/dim]")
        self.run_worker(
            lambda: pmx.analyze_link(url, outcome, side, float(size)),
            thread=True,
            exclusive=True,
            group="analyze",
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "analyze" or event.state != WorkerState.SUCCESS:
            return
        r = event.worker.result
        log = self.query_one("#analyze-log", OutputLog)
        log.clear()
        body = r.get("stdout") or r.get("stderr") or r.get("error") or "No output"
        log.write_block(f"[{r.get('venue', '?')}] analyze", body)
