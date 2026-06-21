from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, ListItem, ListView

NAV_ITEMS = [
    ("home", "Desk", "1"),
    ("chat", "AI", "2"),
    ("analyze", "Link", "3"),
    ("positions", "Pos", "4"),
    ("markets", "Mkt", "5"),
    ("diagnostics", "Diag", "6"),
    ("safety", "Safe", "7"),
    ("audit", "Audit", "8"),
]


class NavSidebar(VerticalScroll):
    DEFAULT_CSS = """
    NavSidebar {
        width: 16;
        height: 1fr;
        background: #050608;
        border-right: solid #1a2332;
        padding: 0;
    }
    ListView {
        height: auto;
    }
    ListItem {
        padding: 0 1;
        height: 1;
    }
    ListItem.-highlight {
        background: #0d1a12;
        color: #00ff9c;
    }
    """

    def compose(self) -> ComposeResult:
        items = [
            ListItem(Label(f"[{key}] {label}"), id=f"nav-{screen_id}")
            for screen_id, label, key in NAV_ITEMS
        ]
        yield ListView(*items, id="nav-list")

    def highlight(self, screen_id: str) -> None:
        lv = self.query_one("#nav-list", ListView)
        for item in lv.children:
            item.remove_class("-highlight")
            if item.id == f"nav-{screen_id}":
                item.add_class("-highlight")
