from __future__ import annotations

import shutil
import subprocess
import sys

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static


def copy_to_clipboard(text: str) -> bool:
    if sys.platform == "darwin" and shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=text.encode(), check=False)
        return True
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text.encode(), check=False)
        return True
    if shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=False)
        return True
    return False


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
            yield Static(f"[bold yellow]{self.warning}[/bold yellow]", markup=True)
            yield Static(self.command, id="confirm-cmd")
            with Horizontal():
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Copy", id="copy")
                yield Button("Run now", variant="error", id="run")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "copy":
            if copy_to_clipboard(self.command):
                self.app.notify("Copied to clipboard")
            else:
                self.app.notify(self.command, title="Copy manually", timeout=10)
            self.dismiss(False)
        elif event.button.id == "run":
            self.dismiss(True)


class PanicConfirmModal(ModalScreen[bool]):
    """Require typing PANIC before emergency flatten."""

    DEFAULT_CSS = """
    PanicConfirmModal {
        align: center middle;
    }
    #panic-box {
        width: 72;
        border: thick $error;
        background: $panel;
        padding: 1 2;
    }
    #panic-input {
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="panic-box"):
            yield Static(
                "[bold red]EMERGENCY PANIC[/bold red]\n"
                "Engages kill switch, cancels orders, market-closes all positions.\n"
                "Type [bold]PANIC[/bold] to confirm.",
                markup=True,
            )
            yield Input(placeholder="Type PANIC", id="panic-input")
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button("Flatten now", variant="error", id="run", disabled=True)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "panic-input":
            ok = event.value.strip() == "PANIC"
            self.query_one("#run", Button).disabled = not ok

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "panic-input" and event.value.strip() == "PANIC":
            self.dismiss(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "run":
            val = self.query_one("#panic-input", Input).value.strip()
            if val == "PANIC":
                self.dismiss(True)
