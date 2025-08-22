import typer
from rich.console import Console
from rich.panel import Panel
import os
from .watcher import PyFileMonitor

app = typer.Typer()


@app.command()
def main(
    folder: str = typer.Argument(
        ".", help="Folder to monitor (default: current directory)"
    ),
    autofix: bool = typer.Option(
        False, "--autofix", help="Enable autofix with ruff check"
    ),
):
    """
    Start the file monitor.
    """
    if folder != "." and folder != "all" and not os.path.isdir(folder):
        Console().print(
            Panel(
                f"Folder '{folder}' does not exist; cannot monitor it.",
                title="error",
                border_style="red",
                title_align="left",
            )
        )
        raise typer.Exit(1)
    path = "." if folder == "all" else folder
    monitor = PyFileMonitor(path=path, autofix=autofix)
    monitor.start()


if __name__ == "__main__":
    app()
