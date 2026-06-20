from __future__ import annotations

from rich.text import Text
from textual.widgets import RichLog

from apps.cockpit.widgets.access_log import access_line


class ActivityLog(RichLog):
    """Shared bottom log — GoAccess-style access log lines."""

    DEFAULT_CSS = """
    ActivityLog {
        height: 4;
        min-height: 3;
        max-height: 6;
        border-top: solid #1a2332;
        background: #050608;
        color: #b8c5d6;
        padding: 0 1;
    }
    """

    def log_command(self, cmd: str, output: str, ok: bool | None = None) -> None:
        self.write(access_line(cmd, output, ok=ok))
        if output.strip() and len(output.splitlines()) > 1:
            for line in output.strip().splitlines()[1:4]:
                self.write(Text(f"  {line[:100]}"))
