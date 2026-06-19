from __future__ import annotations

from textual.widgets import RichLog


class OutputLog(RichLog):
    """Scrollable command output."""

    DEFAULT_CSS = """
    OutputLog {
        height: 1fr;
        border: solid $border;
        background: $surface;
        padding: 0 1;
    }
    """

    def write_block(self, title: str, body: str) -> None:
        if title:
            self.write(f"[bold]{title}[/bold]")
        if body:
            self.write(body.rstrip())
        self.write("")
