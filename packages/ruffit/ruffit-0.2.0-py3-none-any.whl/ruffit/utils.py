import subprocess
from rich.panel import Panel
from datetime import datetime


def run_ruff_format(file_path, console):
    """
    Run ruff format on the given file.
    
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result = subprocess.run(
            ["ruff", "format", file_path], capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print(
                Panel(
                    f"[bold green]formatted:[/bold green] {file_path} [dim]{timestamp}[/dim]",
                    title="[bold]Ruff Format[/bold]",
                    border_style="green",
                    title_align="left",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]ruff format failed for {file_path}: [dim]{timestamp}[/dim][/bold red]\n{result.stderr}",
                    title="[bold]Ruff Format[/bold]",
                    border_style="red",
                    title_align="left",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]error running ruff format: {e}  [dim]{timestamp}[/dim] [/bold red]",
                title="[bold]Ruff Format[/bold]",
                border_style="red",
                title_align="left",
            )
        )


def run_ruff_check(file_path, console, autofix=False):
    """
    Run ruff check on the given file.
    Run with --fix if autofix is enabled.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cmd = ["ruff", "check", file_path]
    if autofix:
        cmd.insert(2, "--fix")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            console.print(
                Panel(
                    f"[bold green]ruff check passed:[/bold green] {file_path} [dim]{timestamp}[/dim]",
                    title="[bold]Ruff Check[/bold]",
                    border_style="green",
                    title_align="left",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]ruff check issues for {file_path}: [dim]{timestamp}[/dim][/bold red]\n{result.stdout}",
                    title="[bold]Ruff Check[/bold]",
                    border_style="red",
                    title_align="left",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]error running ruff check: {e} [dim]{timestamp}[/dim][/bold red]",
                title="[bold]Ruff Check[/bold]",
                border_style="red",
                title_align="left",
            )
        )


def run_ty_check(file_path, console):
    """
    Run ty check on the given file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result = subprocess.run(
            ["ty", "check", file_path], capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print(
                Panel(
                    f"[bold green]ty check passed:[/bold green] {file_path} [dim]{timestamp}[/dim]",
                    title="[bold]Ty Check[/bold]",
                    border_style="green",
                    title_align="left",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]ty check issues for {file_path}: [dim]{timestamp}[/dim][/bold red]\n{result.stdout}",
                    title="[bold]Ty Check[/bold]",
                    border_style="red",
                    title_align="left",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[red]error running ty check: {e} [dim]{timestamp}[/dim] [/red]",
                title="[bold]Ty Check[/bold]",
                border_style="red",
                title_align="left",
            )
        )
