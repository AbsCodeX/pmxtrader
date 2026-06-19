from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, ListItem, ListView

NAV_ITEMS = [
    ("home", "Dashboard", "1"),
    ("chat", "AI Chat", "2"),
    ("analyze", "Analyze", "3"),
    ("positions", "Positions", "4"),
    ("markets", "Markets", "5"),
    ("diagnostics", "Diagnostics", "6"),
    ("safety", "Safety", "7"),
]


class NavSidebar(VerticalScroll):
    DEFAULT_CSS = """
    NavSidebar {
        width: 22;
        height: 1fr;
        background: $panel;
        border-right: solid $border;
        padding: 1 0;
    }
    ListView {
        height: auto;
    }
    ListItem {
        padding: 0 1;
    }
    ListItem.-highlight {
        background: $accent;
        color: $text;
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
