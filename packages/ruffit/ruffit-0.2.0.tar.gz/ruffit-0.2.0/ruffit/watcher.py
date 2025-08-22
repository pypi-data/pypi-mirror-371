from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from .utils import run_ruff_format, run_ruff_check, run_ty_check
from datetime import datetime
import time
import os


class PyFileMonitor(FileSystemEventHandler):
    def __init__(self, path=".", autofix=False):
        self.console = Console()
        self.path = path
        self.autofix = autofix
        self.observer = Observer()
        self.ruffit_dir = os.path.abspath(os.path.dirname(__file__))
        self._event_times = {}
        self._debounce_seconds = 0.5

    def _should_ignore(self, src_path):
        abs_path = os.path.abspath(src_path)
        venv_names = [".venv", "venv", "env", ".env"]
        parts = abs_path.split(os.sep)
        if abs_path.startswith(self.ruffit_dir):
            return True
        if any(name in parts for name in venv_names):
            return True
        return False

    def _debounced(self, src_path):
        now = time.time()
        last_time = self._event_times.get(src_path, 0)
        if now - last_time < self._debounce_seconds:
            return True
        self._event_times[src_path] = now
        return False

    def on_modified(self, event):
        if event.is_directory:
            return
        if str(event.src_path).endswith(".py") and not self._should_ignore(
            event.src_path
        ):
            if not self._debounced(event.src_path):
                self.console.clear()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.console.print(
                    Panel(
                        f"[bold yellow]Modified:[/bold yellow] {event.src_path}  [dim]{timestamp}[/dim]",
                        title="[bold]File Event[/bold]",
                        border_style="yellow",
                        title_align="left",
                    )
                )
                run_ruff_format(event.src_path, self.console)
                run_ruff_check(event.src_path, self.console, autofix=self.autofix)
                run_ty_check(event.src_path, self.console)

    def on_created(self, event):
        if event.is_directory:
            return
        if str(event.src_path).endswith(".py") and not self._should_ignore(
            event.src_path
        ):
            if not self._debounced(event.src_path):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.console.print(
                    Panel(
                        f"[bold yellow]Created:[/bold yellow] {event.src_path} [dim]{timestamp}[/dim]",
                        title="[bold]File Event[/bold]",
                        border_style="yellow",
                        title_align="left",
                    )
                )

    def start(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.print(
            Panel(
                f"[bold blue]ruffit has started; monitoring {os.path.abspath(self.path)} for .py file changes![/bold blue]  [dim]{timestamp}[/dim]",
                title="[bold]Ruffit[/bold]",
                border_style="blue",
                title_align="left",
            )
        )
        if self.autofix:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.console.print(
                Panel(
                    f"[bold blue]autofix is enabled; ruff check will run with --fix[/bold blue]  [dim]{timestamp}[/dim]",
                    title="[bold]Ruffit[/bold]",
                    border_style="blue",
                    title_align="left",
                )
            )
        self.observer.schedule(self, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.console.print(
                Panel(
                    f"[bold red]exiting ruffit.[/bold red]  [dim]{timestamp}[/dim]",
                    title="[bold]Ruffit[/bold]",
                    border_style="red",
                    title_align="left",
                )
            )
            self.observer.stop()
        self.observer.join()
