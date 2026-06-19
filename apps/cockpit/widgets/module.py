"""WTF-style bordered dashboard module."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static


class DashModule(Vertical):
    """Bordered panel with a colored title bar (WTF / sampler module)."""

    DEFAULT_CSS = """
    DashModule {
        border: tall $accent;
        background: $panel;
        height: 1fr;
        min-height: 6;
    }
    DashModule > .mod-title {
        dock: top;
        height: 1;
        background: $accent;
        color: $text;
        text-align: center;
        text-style: bold;
    }
    DashModule > .mod-body {
        height: 1fr;
        padding: 0 1;
    }
    """

    def __init__(self, title: str, *children: Widget, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._children = children

    def compose(self) -> ComposeResult:
        yield Static(self._title, classes="mod-title", markup=True)
        with Vertical(classes="mod-body"):
            yield from self._children
