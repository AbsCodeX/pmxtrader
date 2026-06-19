from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from apps.cockpit.bridge import parse, pmx
from apps.cockpit.widgets.output_log import OutputLog


class HomePane(Vertical):
    DEFAULT_CSS = """
    HomePane {
        padding: 1 0;
    }
    .card-row {
        height: auto;
        margin-bottom: 1;
    }
    .stat-card {
        width: 1fr;
        height: auto;
        border: solid $border;
        background: $panel;
        padding: 1;
        margin: 0 1 0 0;
    }
    .stat-card:last-child {
        margin-right: 0;
    }
    .actions {
        height: auto;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("[bold]Trading dashboard[/bold] — press [cyan]1-6[/cyan] to switch panels")
        with Horizontal(classes="card-row"):
            yield Static("Loading…", id="card-kalshi", classes="stat-card")
            yield Static("Loading…", id="card-poly", classes="stat-card")
            yield Static("Loading…", id="card-session", classes="stat-card")
        with Horizontal(classes="actions"):
            yield Button("Analyze link [a]", id="go-analyze", variant="primary")
            yield Button("AI chat [2]", id="go-chat", variant="success")
            yield Button("Diagnostics [5]", id="go-diag")
            yield Button("Refresh [r]", id="refresh")
            yield Button("Web dashboard", id="go-web")
        yield Static("Output", classes="section-label")
        yield OutputLog(id="home-log", markup=True)

    def on_mount(self) -> None:
        self.refresh_status()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app = self.app
        if event.button.id == "go-analyze":
            app.action_tab("analyze")
        elif event.button.id == "go-chat":
            app.action_tab("chat")
        elif event.button.id == "go-diag":
            app.action_tab("diagnostics")
        elif event.button.id == "refresh":
            self.refresh_status()
        elif event.button.id == "go-web":
            pmx.run_script("pmxt-dashboard.sh", "start")

    def refresh_status(self) -> None:
        r = pmx.run_pmx("status")
        s = parse.parse_status(r.get("stdout") or "")
        self.query_one("#card-kalshi", Static).update(
            f"[bold]Kalshi[/bold]\n"
            f"Kill: [bold]{'red' if s.kill_switch == 'ON' else 'green'}]{s.kill_switch}[/]\n"
            f"Avail: ${s.kalshi_available or '?'}\n"
            f"Total: ${s.kalshi_total or '?'}"
        )
        self.query_one("#card-poly", Static).update(
            f"[bold]Poly US[/bold]\n"
            f"Avail: ${s.poly_available or '?'}\n"
            f"Total: ${s.poly_total or '?'}"
        )
        sidecar = "● live" if r.get("ok") else "○ check diagnostics"
        self.query_one("#card-session", Static).update(
            f"[bold]Session[/bold]\nSidecar: {sidecar}\n[dim]Tab 5 = full health[/dim]"
        )
        log = self.query_one("#home-log", OutputLog)
        log.clear()
        log.write_block("status", r.get("stdout") or r.get("stderr") or r.get("error", ""))
