"""GoAccess-style access log formatting for activity feeds."""

from __future__ import annotations

from datetime import datetime


def access_line(cmd: str, output: str = "", ok: bool | None = None) -> str:
    ts = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
    if ok is None:
        low = output.lower()
        ok = bool(output.strip()) and "error" not in low and "failed" not in low
    code = "200" if ok else "502"
    color = "green" if ok else "red"
    path = cmd if cmd.startswith("./") else f"./pmx {cmd}"
    preview = output.strip().splitlines()[0][:60] if output.strip() else "—"
    return (
        f"[dim]{ts}[/dim] "
        f"[{color}]{code}[/{color}] "
        f"[cyan]{path}[/cyan] "
        f"[dim]{preview}[/dim]"
    )
