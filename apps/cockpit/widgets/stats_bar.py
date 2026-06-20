"""Compact terminal metrics strip — venue balances + health at a glance."""

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
        height: 1;
        border: solid #1a2332;
        background: #050608;
        content-align: center middle;
        padding: 0 1;
    }
    """


class StatsBar(Horizontal):
    """Real-time summary row — Bloomberg-style stat cells."""

    DEFAULT_CSS = """
    StatsBar {
        height: 1;
        margin-bottom: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield _StatCell("[#00ff9c]KAL[/] —", id="s-kalshi", markup=True)
        yield _StatCell("[#00d4ff]POLY[/] —", id="s-poly", markup=True)
        yield _StatCell("[#ffb000]MKT[/] —", id="s-markets", markup=True)
        yield _StatCell("[#c0caf5]HLTH[/] —", id="s-health", markup=True)
        yield _StatCell("[#8b949e]CAR[/] —", id="s-sidecar", markup=True)
        yield _StatCell("[#5a6a7a]CLK[/] —", id="s-updated", markup=True)

    def apply_snapshot(self, snap: LiveSnapshot) -> None:
        ks = snap.kill_switch
        ks_color = "#ff4466" if ks == "ON" else "#00ff9c"
        ro_color = "#ffb000" if snap.read_only else "#00ff9c"
        ro_label = "RO" if snap.read_only else "LIVE"
        self.query_one("#s-kalshi", _StatCell).update(
            f"[#00ff9c]K[/][#eef2f8]${snap.kalshi_available or '?'}[/] [{ks_color}]{ks}[/]"
        )
        self.query_one("#s-poly", _StatCell).update(
            f"[#00d4ff]P[/][#eef2f8]${snap.poly_available or '?'}[/] [{ro_color}]{ro_label}[/]"
        )
        self.query_one("#s-markets", _StatCell).update(
            f"[#ffb000]M[/][#eef2f8]{len(snap.markets)}[/]"
        )
        score = snap.health_score
        total = snap.health_total or 1
        pct = int(score / total * 100)
        h_color = "#00ff9c" if pct >= 80 else ("#ffb000" if pct >= 50 else "#ff4466")
        self.query_one("#s-health", _StatCell).update(
            f"[#c0caf5]H[/][{h_color}]{score}/{total}[/]"
        )
        side = "UP" if snap.sidecar_ok else "DN"
        s_color = "#00ff9c" if snap.sidecar_ok else "#ff4466"
        self.query_one("#s-sidecar", _StatCell).update(
            f"[#8b949e]C[/][{s_color}]{side}[/]"
        )
        self.query_one("#s-updated", _StatCell).update(
            f"[#8b9cb5]{datetime.now().strftime('%H:%M:%S')}[/]"
        )
