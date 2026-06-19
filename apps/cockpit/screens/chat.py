from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, RichLog, Select, Static
from textual.worker import Worker, WorkerState

from apps.cockpit.bridge import ai, pmx
from apps.cockpit.widgets.confirm_modal import ConfirmCommandModal


class ChatPane(Vertical):
    DEFAULT_CSS = """
    ChatPane {
        padding: 1 0;
    }
    #chat-log {
        height: 1fr;
        border: solid $border;
        background: $surface;
        padding: 0 1;
    }
    #chat-input-row {
        height: auto;
        margin-top: 1;
    }
    #chat-input {
        width: 1fr;
    }
    .hint {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    PROVIDERS = [("grok", "Grok (default)"), ("openai", "OpenAI"), ("claude", "Claude")]

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold]AI assistant[/bold] — ask about markets, links, volume, commands. "
            "Trade orders require your confirm.",
            classes="hint",
        )
        with Horizontal():
            yield Select(self.PROVIDERS, id="chat-provider", value="grok")
            yield Button("Clear chat", id="chat-clear")
            yield Button("New session", id="chat-new")
        yield RichLog(id="chat-log", markup=True, wrap=True)
        with Horizontal(id="chat-input-row"):
            yield Input(placeholder="Ask: analyze this link, top poly markets, my balance…", id="chat-input")
            yield Button("Send", variant="primary", id="chat-send")
        yield Static("", id="suggested-cmd")

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write("[dim]Examples: What's my balance? · Analyze kalshi.com/… · Top poly markets soccer[/dim]\n")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "chat-send":
            self._send()
        elif event.button.id == "chat-clear":
            self.query_one("#chat-log", RichLog).clear()
        elif event.button.id == "chat-new":
            ai.clear_session()
            self.query_one("#chat-log", RichLog).clear()
            self.app.notify("New AI session")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat-input":
            self._send()

    def _send(self) -> None:
        inp = self.query_one("#chat-input", Input)
        msg = inp.value.strip()
        if not msg:
            return
        inp.value = ""
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[bold cyan]You:[/bold cyan] {msg}")
        provider = self.query_one("#chat-provider", Select).value or "grok"
        self.run_worker(lambda: ai.chat_turn(msg, str(provider)), thread=True, exclusive=True, group="chat")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "chat" or event.state != WorkerState.SUCCESS:
            return
        result = event.worker.result
        log = self.query_one("#chat-log", RichLog)
        text = result.get("text", "")
        log.write(f"[bold green]AI:[/bold green] {text}\n")
        cmds = pmx.extract_pmx_commands(text)
        if cmds:
            self.query_one("#suggested-cmd", Static).update(
                f"Suggested: [cyan]{cmds[0]}[/cyan] — press [bold]Ctrl+Enter[/bold] to run first safe command"
            )
            self._pending_cmd = cmds[0]
        else:
            self._pending_cmd = None

    _pending_cmd: str | None = None

    def action_run_suggested(self) -> None:
        cmd = getattr(self, "_pending_cmd", None)
        if not cmd:
            return
        self._run_command(cmd)

    def _run_command(self, cmd: str) -> None:
        kind = pmx.classify_command(cmd)
        if kind == "trade":

            def on_confirm(run: bool) -> None:
                if run:
                    self._exec(cmd)

            self.app.push_screen(ConfirmCommandModal(cmd), on_confirm)
        elif kind in ("safe", "unknown"):
            if kind == "unknown":
                self.app.notify("Running command — verify if sensitive", severity="warning")
            self._exec(cmd)
        else:
            self.app.notify("No runnable command", severity="warning")

    def _exec(self, cmd: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        parts = cmd.replace("./pmx ", "").split()
        r = pmx.run_pmx(*parts, timeout=120)
        out = r.get("stdout") or r.get("stderr") or r.get("error") or ""
        log.write(f"[dim]$ {cmd}[/dim]\n{out}\n")
