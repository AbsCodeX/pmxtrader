from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RichLog, Static


class ConfirmCommandModal(ModalScreen[bool]):
    """Confirm before running trade or dangerous commands."""

    DEFAULT_CSS = """
    ConfirmCommandModal {
        align: center middle;
    }
    #confirm-box {
        width: 80;
        height: auto;
        max-height: 80%;
        border: thick $warning;
        background: $panel;
        padding: 1 2;
    }
    #confirm-cmd {
        color: $accent;
        margin: 1 0;
    }
    """

    def __init__(self, command: str, warning: str = "Real money — confirm to run.") -> None:
        super().__init__()
        self.command = command
        self.warning = warning

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-box"):
            yield Static(f"[bold yellow]{self.warning}[/bold yellow]")
            yield Static(self.command, id="confirm-cmd")
            with Horizontal():
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Copy only", id="copy")
                yield Button("Run now", variant="error", id="run")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "copy":
            self.dismiss(False)
            self.app.notify("Copy from output panel — clipboard in terminal varies")
        elif event.button.id == "run":
            self.dismiss(True)
