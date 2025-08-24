import typer
from rich.console import Console
from pathlib import Path
import hashlib

app = typer.Typer(help="Hash checkers (MD5/SHA256)")
console = Console()

@app.command()
def file(path: Path, algo: str = typer.Option("sha256", help="Hash algorithm: md5|sha256")):
    """Compute hash of a file."""
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        console.print(f"[{algo.upper()}] {path}: {h.hexdigest()}")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
