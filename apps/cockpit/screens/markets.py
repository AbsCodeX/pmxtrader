from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge.live import fetch_poly_markets
from apps.cockpit.widgets.output_log import OutputLog
from apps.cockpit.widgets.rich_escape import escape_rich


class MarketsPane(Vertical):
    DEFAULT_CSS = """
    MarketsPane { padding: 0; height: 1fr; }
    #markets-query { width: 1fr; }
    #markets-out { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Poly US markets[/bold]  [dim]Search + live fetch[/dim]", markup=True)
        with Horizontal():
            yield Input(placeholder="Search e.g. world cup, nfl…", id="markets-query")
            yield Button("Search", variant="primary", id="markets-search")
            yield Button("Refresh", id="markets-refresh")
        yield OutputLog(id="markets-out", markup=True)

    def on_mount(self) -> None:
        self.search_markets("")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ("markets-search", "markets-refresh"):
            q = self.query_one("#markets-query", Input).value.strip()
            self.search_markets(q)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "markets-query":
            self.search_markets(event.value.strip())

    def search_markets(self, query: str) -> None:
        log = self.query_one("#markets-out", OutputLog)
        log.clear()
        log.write("[dim]Loading markets…[/dim]")
        self.run_worker(lambda: self._fetch(query), thread=True, exclusive=True, group="markets")

    def _fetch(self, query: str) -> str:
        rows = fetch_poly_markets(query, limit=20)
        if rows:
            lines = ["[bold]Market[/bold]          [bold]Slug[/bold]                    [bold]Vol[/bold]   [bold]Price[/bold]"]
            for m in rows:
                lines.append(
                    f"{escape_rich(m.get('title', '')[:28]):28}  "
                    f"{escape_rich(m.get('slug', '')[:26]):26}  "
                    f"{escape_rich(str(m.get('volume', ''))):8}  "
                    f"{escape_rich(str(m.get('price', '')))}"
                )
            lines.append("\n[dim]Analyze: ./pmx poly quote SLUG long[/dim]")
            return "\n".join(lines)
        return "No markets returned — check sidecar and Poly US keys."

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "markets":
            return
        log = self.query_one("#markets-out", OutputLog)
        if event.state == WorkerState.ERROR:
            log.clear()
            log.write("[red]Failed to load markets[/red]")
            if event.worker.error:
                log.write_safe(str(event.worker.error))
            self.app.notify("Failed to load markets", severity="error")
            return
        if event.state != WorkerState.SUCCESS:
            return
        log.clear()
        log.write(event.worker.result)
