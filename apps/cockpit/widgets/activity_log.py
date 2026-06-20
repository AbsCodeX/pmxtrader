from __future__ import annotations

from textual.widgets import RichLog

from apps.cockpit.widgets.access_log import access_line


class ActivityLog(RichLog):
    """Shared bottom log — GoAccess-style access log lines."""

    DEFAULT_CSS = """
    ActivityLog {
        height: 8;
        min-height: 5;
        max-height: 12;
        border-top: solid #30363d;
        background: #0d1117;
        color: #c9d1d9;
        padding: 0 1;
    }
    """

    def log_command(self, cmd: str, output: str, ok: bool | None = None) -> None:
        self.write(access_line(cmd, output, ok=ok))
        if output.strip() and len(output.splitlines()) > 1:
            for line in output.strip().splitlines()[1:4]:
                self.write(f"  {line[:100]}", markup=False)
