from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, RichLog, Static
from textual.worker import Worker, WorkerState

from apps.bridge.trade_audit import audit_log_paths, format_audit_entry, tail_jsonl
from apps.cockpit.bridge import pmx


class AuditPane(Vertical):
    DEFAULT_CSS = """
    AuditPane { padding: 0; }
    #audit-log { height: 1fr; border: solid #1a2332; }
    """

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold]Trade audit[/bold] — tail of briefs/alerts/*.jsonl (read-only)",
            markup=True,
        )
        yield Button("Refresh", id="audit-refresh", variant="primary")
        yield RichLog(id="audit-log", markup=True, wrap=True, highlight=False)
        yield Static("", id="audit-summary", markup=True)

    def on_mount(self) -> None:
        self.reload()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "audit-refresh":
            self.reload()

    def reload(self) -> None:
        self.query_one("#audit-summary", Static).update("[dim]Loading…[/dim]")
        self.run_worker(self._load, thread=True, exclusive=True, group="audit")

    def _load(self) -> tuple[list[str], str]:
        root = pmx.ROOT
        lines: list[str] = []
        total = 0
        for label, path in audit_log_paths(root).items():
            rows = tail_jsonl(path, limit=30)
            total += len(rows)
            lines.append(f"[bold cyan]{label}[/] ({path.name})")
            if not path.is_file():
                lines.append("  [dim](file not created yet)[/dim]")
                continue
            if not rows:
                lines.append("  [dim](empty)[/dim]")
                continue
            for row in rows:
                lines.append(f"  {format_audit_entry(row)}")
            lines.append("")
        summary = f"{total} recent entr{'y' if total == 1 else 'ies'} from audit logs"
        return lines, summary

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "audit":
            return
        log = self.query_one("#audit-log", RichLog)
        summary = self.query_one("#audit-summary", Static)
        if event.state == WorkerState.ERROR:
            summary.update("[red]Failed to load audit logs[/red]")
            return
        if event.state != WorkerState.SUCCESS:
            return
        lines, text = event.worker.result
        log.clear()
        for line in lines:
            log.write(line)
        summary.update(text)
