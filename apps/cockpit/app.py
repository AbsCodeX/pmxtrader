from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import ContentSwitcher, Footer, Header, Input, ListItem, ListView, RichLog, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge import pmx
from apps.cockpit.bridge.live import LiveSnapshot, fetch_dashboard
from apps.cockpit.screens.analyze import AnalyzePane
from apps.cockpit.screens.chat import ChatPane
from apps.cockpit.screens.diagnostics import DiagnosticsPane
from apps.cockpit.screens.home import HomePane
from apps.cockpit.screens.markets import MarketsPane
from apps.cockpit.screens.positions import PositionsPane
from apps.cockpit.screens.safety import SafetyPane
from apps.cockpit.widgets.activity_log import ActivityLog
from apps.cockpit.widgets.confirm_modal import ConfirmCommandModal
from apps.cockpit.widgets.nav import NAV_ITEMS, NavSidebar
from apps.cockpit.widgets.ticker_bar import TickerBar

COMMANDS = [
    ("status", "Kill switch + balances"),
    ("balance", "Kalshi cash"),
    ("poly balance", "Poly US cash"),
    ("poly positions", "Poly holdings"),
    ("poly markets", "Search Poly US markets"),
    ("poly orders", "Open Poly orders"),
    ("warm", "Warm sidecar"),
    ("preflight", "GO / NO-GO checklist"),
    ("help", "Full command list"),
    ("dashboard", "Start web dashboard (background)"),
]

SCREEN_IDS = [item[0] for item in NAV_ITEMS]


class CommandPalette(ModalScreen[None]):
    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    CommandPalette { align: center top; padding-top: 2; }
    #palette-box {
        width: 72;
        height: auto;
        max-height: 70%;
        border: solid #00d4ff;
        background: #0a0e14;
        color: #e0e8f0;
        padding: 1 2;
    }
    #palette-list { height: auto; max-height: 18; margin-top: 1; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="palette-box"):
            yield Static("[bold]Command search[/bold] — safe commands only", markup=True)
            yield Input(placeholder="status · poly markets · balance…", id="palette-input")
            yield ListView(id="palette-list")

    def on_mount(self) -> None:
        self._cmd_by_slug: dict[str, str] = {}
        self._filter("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "palette-input":
            self._filter(event.value)

    def _filter(self, query: str) -> None:
        lv = self.query_one("#palette-list", ListView)
        lv.clear()
        self._cmd_by_slug.clear()
        q = query.lower()
        for cmd, desc in COMMANDS:
            if q and q not in cmd and q not in desc.lower():
                continue
            slug = cmd.replace(" ", "-")
            self._cmd_by_slug[slug] = cmd
            lv.append(ListItem(Static(f"./pmx {cmd}  [dim]{desc}[/dim]", markup=True), id=f"cmd:{slug}"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if item_id.startswith("cmd:"):
            slug = item_id[4:]
            cmd = self._cmd_by_slug.get(slug, slug.replace("-", " "))
            self._run(cmd)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "palette-input":
            return
        raw = event.value.strip().removeprefix("./pmx ").strip()
        if raw:
            self._run(raw)

    def _run(self, cmd: str) -> None:
        self.dismiss(None)
        if cmd == "dashboard":
            self.app.push_screen(
                ConfirmCommandModal(
                    "./scripts/pmxt-dashboard.sh start-bg",
                    "Start web dashboard in background?",
                ),
                self._on_dashboard_confirmed,
            )
            return
        if not pmx.is_palette_allowed(cmd):
            self.app.notify("Not allowed in palette — use Terminal or Safety tab", severity="warning")
            return
        parts = cmd.split()
        self.app.run_palette_command(parts)

    def _on_dashboard_confirmed(self, ok: bool) -> None:
        if ok:
            pmx.run_script("pmxt-dashboard.sh", "start-bg")
            self.app.notify("Dashboard starting in background")


class CockpitApp(App):
    CSS_PATH = Path(__file__).parent / "theme.tcss"
    TITLE = "pmxtrader"
    SUB_TITLE = "prediction market terminal"

    BINDINGS = [
        Binding("1", "tab('home')", "Dashboard", show=True),
        Binding("2", "tab('chat')", "Chat", show=True),
        Binding("3", "tab('analyze')", "Analyze", show=True),
        Binding("4", "tab('positions')", "Pos", show=True),
        Binding("5", "tab('markets')", "Markets", show=True),
        Binding("6", "tab('diagnostics')", "Diag", show=True),
        Binding("7", "tab('safety')", "Safety", show=True),
        Binding("slash", "palette", "Search", show=True),
        Binding("ctrl+p", "palette", "Search", show=False),
        Binding("r", "refresh_all", "Refresh", show=True),
        Binding("ctrl+enter", "run_suggested", "Run", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    _current = "home"
    _last_snap: LiveSnapshot | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield TickerBar(id="ticker")
        with Horizontal(id="main-row"):
            yield NavSidebar(id="nav")
            with ContentSwitcher(initial="home", id="switcher"):
                yield HomePane(id="home")
                yield ChatPane(id="chat")
                yield AnalyzePane(id="analyze")
                yield PositionsPane(id="positions")
                yield MarketsPane(id="markets")
                yield DiagnosticsPane(id="diagnostics")
                yield SafetyPane(id="safety")
        yield ActivityLog(id="activity", markup=True, wrap=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#nav", NavSidebar).highlight("home")
        self.set_interval(8.0, self.poll_live)
        self.poll_live()

    def poll_live(self) -> None:
        self.run_worker(fetch_dashboard, thread=True, exclusive=True, group="live-poll")

    def run_palette_command(self, parts: list[str]) -> None:
        label = "./pmx " + " ".join(parts)

        def work() -> dict:
            result = pmx.run_pmx(*parts)
            result["_label"] = label
            return result

        self.run_worker(work, thread=True, group="palette")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group == "live-poll":
            if event.state == WorkerState.ERROR:
                self.notify("Live refresh failed", severity="error")
                return
            if event.state != WorkerState.SUCCESS:
                return
            snap: LiveSnapshot = event.worker.result
            self._last_snap = snap
            self.update_live_bar(snap)
            if self._current == "home":
                try:
                    self.query_one(HomePane).render_snap(snap)
                except Exception as exc:  # noqa: BLE001
                    self.log(f"home render failed: {exc}")
            return

        if event.worker.group == "palette":
            if event.state == WorkerState.ERROR:
                self.notify("Command failed", severity="error")
                return
            if event.state != WorkerState.SUCCESS:
                return
            r = event.worker.result
            cmd = r.get("_label", r.get("command", "./pmx"))
            out = r.get("stdout") or r.get("stderr") or ""
            self.log_activity(cmd, out, ok=r.get("ok"))
            if r.get("ok"):
                self.notify("Command completed")
            else:
                self.notify("Command failed", severity="warning")
            return

    def update_live_bar(self, snap: LiveSnapshot) -> None:
        try:
            self.query_one("#ticker", TickerBar).apply_snapshot(snap)
        except Exception as exc:  # noqa: BLE001
            self.log(f"ticker update failed: {exc}")

    def log_activity(self, cmd: str, output: str, ok: bool | None = None) -> None:
        from apps.cockpit.widgets.access_log import access_line

        try:
            log = self.query_one("#activity", ActivityLog)
            log.log_command(cmd, output, ok=ok)
            if self._current == "home":
                act = self.query_one(HomePane).query_one("#mod-activity-log", RichLog)
                act.write(access_line(cmd, output, ok=ok))
        except Exception as exc:  # noqa: BLE001
            self.log(f"activity log failed: {exc}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "nav-list":
            return
        item_id = event.item.id or ""
        if item_id.startswith("nav-"):
            self.action_tab(item_id[4:])

    def action_tab(self, screen_id: str) -> None:
        if screen_id not in SCREEN_IDS:
            return
        self._current = screen_id
        self.query_one("#switcher", ContentSwitcher).current = screen_id
        self.query_one("#nav", NavSidebar).highlight(screen_id)
        if screen_id == "home" and self._last_snap is not None:
            try:
                self.query_one(HomePane).render_snap(self._last_snap)
            except Exception as exc:  # noqa: BLE001
                self.log(f"home render failed: {exc}")

    def open_analyze(self, url: str = "", *, run: bool = False) -> None:
        from textual.widgets import Input

        self.action_tab("analyze")
        pane = self.query_one(AnalyzePane)
        if url:
            pane.query_one("#analyze-url", Input).value = url
        if run and url:
            pane.run_analysis()

    def action_palette(self) -> None:
        self.push_screen(CommandPalette())

    def action_refresh_all(self) -> None:
        self.poll_live()
        if self._current == "positions":
            self.query_one(PositionsPane).reload_positions()
        elif self._current == "markets":
            self.query_one(MarketsPane).search_markets("")
        elif self._current == "diagnostics":
            self.query_one(DiagnosticsPane).run_checks()

    def action_run_suggested(self) -> None:
        try:
            self.query_one(ChatPane).action_run_suggested()
        except Exception as exc:  # noqa: BLE001
            self.log(f"suggested command failed: {exc}")


def main() -> None:
    import os

    os.chdir(ROOT)
    os.environ.setdefault("PMXTRADER_ROOT", str(ROOT))
    CockpitApp().run()


if __name__ == "__main__":
    main()
