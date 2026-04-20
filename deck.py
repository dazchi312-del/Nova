# deck.py
import requests
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Label
from textual import work

API_URL = "http://127.0.0.1:8000"

class NovaDeck(App):
    """A cyberpunk terminal interface for Project Nova."""
    
    # CSS styling for the terminal interface
    CSS = """
    #telemetry-bar {
        height: 3;
        content-align: center middle;
        background: $panel;
        color: $success;
        border-bottom: solid $primary;
    }
    RichLog {
        background: $surface;
        color: $text;
        padding: 1 2;
    }
    Input {
        dock: bottom;
        border-top: solid $primary;
    }
    """
    
    BINDINGS = [("ctrl+c", "quit", "Disconnect")]

    def __init__(self):
        super().__init__()
        self.session_id = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Initializing Telemetry...", id="telemetry-bar")
        yield RichLog(id="chat-log", markup=True)
        yield Input(placeholder="Jack in. Type a message...", id="chat-input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "NOVA CYBER DECK v0.11.0"
        self.init_session()
        # Ping the API every 2 seconds for live hardware stats
        self.set_interval(2.0, self.update_telemetry)

    @work(thread=True)
    def init_session(self):
        try:
            r = requests.get(f"{API_URL}/session/new")
            self.session_id = r.json()["session_id"]
            log = self.query_one(RichLog)
            self.call_from_thread(log.write, f"[bold green]Uplink Established. Session: {self.session_id}[/bold green]\n")
        except Exception as e:
            log = self.query_one(RichLog)
            self.call_from_thread(log.write, f"[bold red]Failed to connect to API (Is nova.py running?): {e}[/bold red]")

    @work(thread=True)
    def update_telemetry(self):
        try:
            r = requests.get(f"{API_URL}/telemetry")
            data = r.json()
            status = data.get("status", "Unknown")
            color = "green" if data.get("hardware_safe") else "red"
            label = self.query_one("#telemetry-bar", Label)
            self.call_from_thread(label.update, f"[{color}]LIVE TELEMETRY: {status}[/{color}]")
        except Exception:
            pass # Fail silently to avoid spamming the UI if the engine restarts

    @work(thread=True)
    def send_message(self, message: str):
        log = self.query_one(RichLog)
        self.call_from_thread(log.write, f"[bold cyan]Daz:[/bold cyan] {message}")
        
        if not self.session_id:
            return

        try:
            r = requests.post(
                f"{API_URL}/chat", 
                json={"session_id": self.session_id, "message": message}
            )
            data = r.json()
            response = data.get("response", "")
            score = data.get("score", 0.0)
            self.call_from_thread(log.write, f"\n[bold magenta]Nova:[/bold magenta] {response}")
            self.call_from_thread(log.write, f"[dim]Reflector Score: {score:.2f}[/dim]\n")
            self.call_from_thread(log.write, "---")
        except Exception as e:
            self.call_from_thread(log.write, f"\n[bold red]Connection Error: {e}[/bold red]\n")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not event.value.strip(): return
        self.send_message(event.value)
        event.input.value = ""

if __name__ == "__main__":
    app = NovaDeck()
    app.run()