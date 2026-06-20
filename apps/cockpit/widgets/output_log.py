from __future__ import annotations

from textual.widgets import RichLog

from apps.cockpit.widgets.rich_escape import escape_rich


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

    def write_safe(self, text: str) -> None:
        self.write(text, markup=False)

    def write_block(self, title: str, body: str) -> None:
        if title:
            self.write(f"[bold]{escape_rich(title)}[/bold]")
        if body:
            self.write(body.rstrip(), markup=False)
        self.write("")
