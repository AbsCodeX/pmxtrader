"""GoAccess-style summary metrics strip — big numbers in bordered cells."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from apps.cockpit.bridge.live import LiveSnapshot


class _StatCell(Static):
    DEFAULT_CSS = """
    _StatCell {
        width: 1fr;
        height: 3;
        border: solid #30363d;
        background: #0d1117;
        content-align: center middle;
        padding: 0 1;
    }
    .stat-label {
        color: #58a6ff;
        text-style: bold;
        text-align: center;
    }
    .stat-value {
        text-align: center;
        text-style: bold;
    }
    .stat-ok { color: #3fb950; }
    .stat-warn { color: #d29922; }
    .stat-bad { color: #f85149; }
    .stat-cyan { color: #39c5cf; }
    """


class StatsBar(Horizontal):
    """Real-time summary row inspired by GoAccess general statistics panel."""

    DEFAULT_CSS = """
    StatsBar {
        height: 3;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield _StatCell("[#58a6ff]KALSHI[/]\n—", id="s-kalshi", markup=True)
        yield _StatCell("[dim]POLY US[/dim]\n—", id="s-poly", markup=True)
        yield _StatCell("[dim]MARKETS[/dim]\n—", id="s-markets", markup=True)
        yield _StatCell("[dim]HEALTH[/dim]\n—", id="s-health", markup=True)
        yield _StatCell("[dim]SIDECAR[/dim]\n—", id="s-sidecar", markup=True)
        yield _StatCell("[dim]UPDATED[/dim]\n—", id="s-updated", markup=True)

    def apply_snapshot(self, snap: LiveSnapshot) -> None:
        ks = snap.kill_switch
        ks_cls = "stat-bad" if ks == "ON" else "stat-ok"
        ro_cls = "stat-warn" if snap.read_only else "stat-ok"
        ro_label = "RO" if snap.read_only else "LIVE"
        self.query_one("#s-kalshi", _StatCell).update(
            f"[#58a6ff]KALSHI[/]\n[bold]${snap.kalshi_available or '?'}[/] [{ks_cls}]{ks}[/]"
        )
        self.query_one("#s-poly", _StatCell).update(
            f"[#58a6ff]POLY US[/]\n[bold]${snap.poly_available or '?'}[/] [{ro_cls}]{ro_label}[/]"
        )
        self.query_one("#s-markets", _StatCell).update(
            f"[#58a6ff]MARKETS[/]\n[bold][#39c5cf]{len(snap.markets)}[/][/]"
        )
        score = snap.health_score
        total = snap.health_total or 1
        pct = int(score / total * 100)
        h_cls = "stat-ok" if pct >= 80 else ("stat-warn" if pct >= 50 else "stat-bad")
        self.query_one("#s-health", _StatCell).update(
            f"[#58a6ff]HEALTH[/]\n[bold {h_cls}]{score}/{total}[/] [dim]{pct}%[/dim]"
        )
        side = "LIVE" if snap.sidecar_ok else "DOWN"
        s_cls = "stat-ok" if snap.sidecar_ok else "stat-bad"
        self.query_one("#s-sidecar", _StatCell).update(
            f"[#58a6ff]SIDECAR[/]\n[bold {s_cls}]{side}[/]"
        )
        self.query_one("#s-updated", _StatCell).update(
            f"[#58a6ff]UPDATED[/]\n[dim]{datetime.now().strftime('%H:%M:%S')}[/]"
        )
