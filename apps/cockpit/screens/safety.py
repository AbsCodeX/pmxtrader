from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static

from apps.cockpit.bridge import pmx
from apps.cockpit.widgets.confirm_modal import ConfirmCommandModal
from apps.cockpit.widgets.output_log import OutputLog


class SafetyPane(Vertical):
    DEFAULT_CSS = """
    SafetyPane { padding: 1 0; }
    .warn { color: $warning; margin: 1 0; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Safety controls[/bold]")
        yield Static("Block new trades or emergency flatten. Trades always need confirm.", classes="warn")
        with Horizontal():
            yield Input(placeholder='Stop reason e.g. "halftime"', id="stop-reason")
            yield Button("Stop trading", variant="warning", id="btn-stop")
            yield Button("Resume trading", id="btn-resume")
        with Horizontal():
            yield Button("PANIC — flatten all", variant="error", id="btn-panic")
            yield Button("Status", id="btn-status")
        yield OutputLog(id="safety-log", markup=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-stop":
            reason = self.query_one("#stop-reason", Input).value.strip() or "manual"
            self._run_safe(["stop", "on", reason])
        elif bid == "btn-resume":
            self._run_safe(["resume"])
        elif bid == "btn-panic":
            self.app.push_screen(
                ConfirmCommandModal("./pmx panic", "PANIC — type confirms in subprocess. Real flatten."),
                lambda ok: self._run_safe(["panic"]) if ok else None,
            )
        elif bid == "btn-status":
            self._run_safe(["status"])

    def _run_safe(self, args: list[str]) -> None:
        r = pmx.run_pmx(*args)
        log = self.query_one("#safety-log", OutputLog)
        log.write_block(" ".join(args), r.get("stdout") or r.get("stderr") or "")
