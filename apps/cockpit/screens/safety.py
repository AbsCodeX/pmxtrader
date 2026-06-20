from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge import pmx
from apps.cockpit.widgets.confirm_modal import ConfirmCommandModal, PanicConfirmModal
from apps.cockpit.widgets.output_log import OutputLog


class SafetyPane(Vertical):
    DEFAULT_CSS = """
    SafetyPane { padding: 1 0; }
    .warn { color: $warning; margin: 1 0; }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Safety controls[/bold]")
        yield Static("Block new trades or emergency flatten. Trades always need confirm.", classes="warn")
        yield Static("", id="safety-status", markup=True)
        with Horizontal():
            yield Input(placeholder='Stop reason e.g. "halftime"', id="stop-reason")
            yield Button("Stop trading", variant="warning", id="btn-stop")
            yield Button("Resume trading", id="btn-resume")
        with Horizontal():
            yield Button("PANIC — flatten all", variant="error", id="btn-panic")
            yield Button("Status", id="btn-status")
        yield OutputLog(id="safety-log", markup=True)

    def on_mount(self) -> None:
        self._refresh_safety_status()

    def _refresh_safety_status(self) -> None:
        from apps.bridge.trade_safety import safety_snapshot

        snap = safety_snapshot(pmx.ROOT)
        ks = snap.kill_switch
        ks_style = "red" if ks == "ON" else "green"
        ro_style = "yellow" if snap.read_only else "green"
        ro = "ON" if snap.read_only else "OFF"
        max_sz = int(snap.max_trade_contracts or 10)
        reason = f" — {snap.kill_switch_reason}" if snap.kill_switch_reason else ""
        self.query_one("#safety-status", Static).update(
            f"Kill switch: [{ks_style}]{ks}[/]  "
            f"Read-only: [{ro_style}]{ro}[/]  "
            f"Max size: [bold]{max_sz}[/] contracts/order{reason}"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-stop":
            reason = self.query_one("#stop-reason", Input).value.strip() or "manual"
            self._run(["stop", "on", reason])
        elif bid == "btn-resume":

            def on_confirm(ok: bool) -> None:
                if ok:
                    self._run(["resume"])

            self.app.push_screen(
                ConfirmCommandModal("./pmx resume", "Resume trading — new orders allowed."),
                on_confirm,
            )
        elif bid == "btn-panic":
            self.app.push_screen(PanicConfirmModal(), self._on_panic_confirmed)
        elif bid == "btn-status":
            self._run(["status"])

    def _on_panic_confirmed(self, ok: bool) -> None:
        if ok:
            self._run(["panic", "--yes"])

    def _run(self, args: list[str]) -> None:
        log = self.query_one("#safety-log", OutputLog)
        log.write("[dim]Running…[/dim]")
        self.run_worker(lambda: pmx.run_pmx(*args), thread=True, exclusive=True, group="safety")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "safety":
            return
        log = self.query_one("#safety-log", OutputLog)
        if event.state == WorkerState.ERROR:
            log.write("[red]Command failed[/red]")
            return
        if event.state != WorkerState.SUCCESS:
            return
        r = event.worker.result
        log.clear()
        log.write_block(r.get("command", "pmx").replace(str(pmx.ROOT / "pmx"), "./pmx"), r.get("stdout") or r.get("stderr") or "")
        self._refresh_safety_status()
