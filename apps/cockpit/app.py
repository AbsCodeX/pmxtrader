from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, ListItem, ListView, Static, TabbedContent, TabPane

from apps.cockpit.screens.analyze import AnalyzePane
from apps.cockpit.screens.chat import ChatPane
from apps.cockpit.screens.diagnostics import DiagnosticsPane
from apps.cockpit.screens.home import HomePane
from apps.cockpit.screens.positions import PositionsPane
from apps.cockpit.screens.safety import SafetyPane
from apps.cockpit.bridge import pmx

COMMANDS = [
    ("status", "Kill switch + balances"),
    ("balance", "Kalshi cash"),
    ("poly balance", "Poly US cash"),
    ("poly positions", "Poly holdings"),
    ("poly markets", "Search Poly US markets"),
    ("poly orders", "Open Poly orders"),
    ("warm", "Warm sidecar"),
    ("scout grok", "Scout research agent"),
    ("dashboard", "Open web dashboard"),
    ("help", "Full command list"),
]

TAB_IDS = ["home", "chat", "analyze", "positions", "diagnostics", "safety"]


class CommandPalette(ModalScreen[None]):
    """Quick command search — type to filter, Enter to run."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    CommandPalette { align: center top; padding-top: 2; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="palette-box"):
            yield Static("[bold]Command palette[/bold] — Enter runs safe ./pmx command")
            yield Input(placeholder="Search: balance, poly markets, status…", id="palette-input")
            yield ListView(id="palette-list")

    def on_mount(self) -> None:
        self._refresh("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "palette-input":
            self._refresh(event.value)

    def _refresh(self, query: str) -> None:
        lv = self.query_one("#palette-list", ListView)
        lv.clear()
        q = query.lower()
        for cmd, desc in COMMANDS:
            if q and q not in cmd and q not in desc.lower():
                continue
            lv.append(ListItem(Static(f"[cyan]./pmx {cmd}[/cyan]  [dim]{desc}[/dim]"), id=f"cmd:{cmd}"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if item_id.startswith("cmd:"):
            cmd = item_id[4:]
            self.dismiss(None)
            app = self.app
            if cmd == "dashboard":
                pmx.run_script("pmxt-dashboard.sh", "start")
            else:
                parts = cmd.split()
                r = pmx.run_pmx(*parts)
                app.notify(r.get("stdout", "")[:80] or "done")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "palette-input":
            return
        raw = event.value.strip()
        if raw.startswith("./pmx "):
            raw = raw[6:]
        if raw:
            parts = raw.split()
            kind = pmx.classify_command("./pmx " + raw)
            self.dismiss(None)
            if kind == "trade":
                self.app.notify("Use Safety tab or confirm in Chat for trades", severity="warning")
            else:
                r = pmx.run_pmx(*parts)
                self.app.notify((r.get("stdout") or "")[:100] or "done")


class CockpitApp(App):
    CSS_PATH = Path(__file__).parent / "theme.tcss"
    TITLE = "pmxtrader cockpit"
    SUB_TITLE = "Kalshi · Poly US · AI · Diagnostics"

    BINDINGS = [
        Binding("1", "tab('home')", "Home", show=True),
        Binding("2", "tab('chat')", "Chat", show=True),
        Binding("3", "tab('analyze')", "Analyze", show=True),
        Binding("4", "tab('positions')", "Positions", show=True),
        Binding("5", "tab('diagnostics')", "Diagnostics", show=True),
        Binding("6", "tab('safety')", "Safety", show=True),
        Binding("slash", "palette", "Search", show=True),
        Binding("ctrl+p", "palette", "Search", show=False),
        Binding("r", "refresh_home", "Refresh", show=True),
        Binding("ctrl+enter", "run_suggested", "Run cmd", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="home", id="main-tabs"):
            with TabPane("Home", id="home"):
                yield HomePane()
            with TabPane("Chat", id="chat"):
                yield ChatPane()
            with TabPane("Analyze", id="analyze"):
                yield AnalyzePane()
            with TabPane("Positions", id="positions"):
                yield PositionsPane()
            with TabPane("Diagnostics", id="diagnostics"):
                yield DiagnosticsPane()
            with TabPane("Safety", id="safety"):
                yield SafetyPane()
        yield Footer()

    def action_tab(self, tab_id: str) -> None:
        if tab_id in TAB_IDS:
            self.query_one("#main-tabs", TabbedContent).active = tab_id

    def action_palette(self) -> None:
        self.push_screen(CommandPalette())

    def action_refresh_home(self) -> None:
        try:
            home = self.query_one(HomePane)
            home.refresh_status()
        except Exception:  # noqa: BLE001
            self.notify("Switch to Home tab to refresh", severity="information")

    def action_run_suggested(self) -> None:
        try:
            chat = self.query_one(ChatPane)
            chat.action_run_suggested()
        except Exception:  # noqa: BLE001
            pass


def main() -> None:
    import os

    os.chdir(ROOT)
    os.environ.setdefault("PMXTRADER_ROOT", str(ROOT))
    CockpitApp().run()


if __name__ == "__main__":
    main()
