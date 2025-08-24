import typer
from rich.console import Console
from pathlib import Path
from pcsuite.core.secure_delete import secure_delete

app = typer.Typer(help="Secure file deletion (multi-pass wipe)")
console = Console()

@app.command()
def file(path: Path, passes: int = typer.Option(3, help="Number of overwrite passes")):
    """Securely delete a file (multi-pass overwrite)."""
    ok = secure_delete(path, passes)
    if ok:
        console.print(f"[green]Securely deleted:[/] {path}")
    else:
        console.print(f"[red]Failed to securely delete:[/] {path}")
