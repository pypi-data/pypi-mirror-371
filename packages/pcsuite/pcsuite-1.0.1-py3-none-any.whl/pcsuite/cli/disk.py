import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import os
import hashlib

app = typer.Typer(help="Disk usage, large file finder, duplicate finder")
console = Console()

@app.command()
def usage(path: Path = typer.Argument(Path.cwd(), help="Directory to scan")):
    """Show disk usage by folder (recursive, top-level only)."""
    table = Table(title=f"Disk Usage: {path}")
    table.add_column("Folder")
    table.add_column("Size (bytes)", justify="right")
    for p in path.iterdir():
        if p.is_dir():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            table.add_row(str(p.name), f"{size:,}")
    console.print(table)

@app.command()
def large(path: Path = typer.Argument(Path.cwd(), help="Directory to scan"), n: int = typer.Option(10, help="Show top N largest files")):
    """Find the largest files in a directory tree."""
    files = [(f, f.stat().st_size) for f in path.rglob("*") if f.is_file()]
    files.sort(key=lambda x: x[1], reverse=True)
    table = Table(title=f"Top {n} Largest Files in {path}")
    table.add_column("File")
    table.add_column("Size (bytes)", justify="right")
    for f, sz in files[:n]:
        table.add_row(str(f), f"{sz:,}")
    console.print(table)

@app.command()
def dupes(path: Path = typer.Argument(Path.cwd(), help="Directory to scan")):
    """Find duplicate files by hash (SHA256)."""
    hashes = {}
    for f in path.rglob("*"):
        if f.is_file():
            h = hashlib.sha256()
            try:
                with open(f, "rb") as fp:
                    while chunk := fp.read(8192):
                        h.update(chunk)
                digest = h.hexdigest()
                hashes.setdefault(digest, []).append(f)
            except Exception:
                continue
    table = Table(title=f"Duplicate Files in {path}")
    table.add_column("SHA256")
    table.add_column("Files")
    for digest, files in hashes.items():
        if len(files) > 1:
            table.add_row(digest, "\n".join(str(f) for f in files))
    console.print(table)
