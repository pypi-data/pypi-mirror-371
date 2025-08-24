from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
import shutil
import os
import time
from pcsuite.core import fs

app = typer.Typer(help="Quarantine management tools")
console = Console()

QUAR_DIR = Path.cwd() / "Quarantine"

@app.command()
def list():
    """List all files in quarantine with metadata."""
    if not QUAR_DIR.exists():
        console.print("[yellow]No quarantine directory found.[/]")
        return
    table = Table(title="Quarantined Files")
    table.add_column("File")
    table.add_column("Size", justify="right")
    table.add_column("Quarantined At")
    table.add_column("Original Path")
    table.add_column("SHA256")
    for f in QUAR_DIR.iterdir():
        if f.is_file() and not f.name.endswith(".meta.json"):
            stat = f.stat()
            meta = f.with_suffix(f.suffix + ".meta.json")
            orig = sha256 = ""
            if meta.exists():
                try:
                    import json
                    with open(meta, "r", encoding="utf-8") as m:
                        md = json.load(m)
                        orig = md.get("original_path", "")
                        sha256 = md.get("sha256", "")
                except Exception:
                    pass
            table.add_row(f.name, f"{stat.st_size:,}", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime)), orig, sha256)
    console.print(table)

@app.command()
def inspect(filename: str):
    """Show metadata for a quarantined file."""
    f = QUAR_DIR / filename
    meta = f.with_suffix(f.suffix + ".meta.json")
    if not meta.exists():
        console.print(f"[yellow]No metadata found for:[/] {filename}")
        raise typer.Exit(1)
    import json
    with open(meta, "r", encoding="utf-8") as m:
        md = json.load(m)
    console.print(md)
@app.command()
def restore(filename: str, to: Path = typer.Option(None, help="Restore to this path (default: original location if known)")):
    """Restore a quarantined file to its original location or a specified path."""
    f = QUAR_DIR / filename
    if not f.exists():
        console.print(f"[red]File not found in quarantine:[/] {filename}")
        raise typer.Exit(1)
    meta = f.with_suffix(f.suffix + ".meta.json")
    orig = None
    if meta.exists():
        try:
            import json
            with open(meta, "r", encoding="utf-8") as m:
                md = json.load(m)
                orig = md.get("original_path")
        except Exception:
            pass
    target = to or orig
    if not target:
        console.print("[red]No destination specified and original path unknown.")
        raise typer.Exit(1)
    target_path = Path(target)
    if not target_path.parent.exists():
        console.print(f"[red]Original directory does not exist. Use --to to specify a destination.")
        raise typer.Exit(2)
    shutil.move(str(f), str(target_path))
    if meta.exists():
        meta.unlink()
    console.print(f"[green]Restored:[/] {filename} -> {target_path}")

@app.command()
def purge(
    days: int = typer.Option(30, help="Purge quarantined files older than this many days"),
    yes: bool = typer.Option(False, "--yes", help="Confirm purge without prompting")
):
    """Delete quarantined files older than N days."""
    if not yes:
        confirm = typer.confirm(f"Are you sure you want to permanently delete quarantined files older than {days} days?")
        if not confirm:
            console.print("[green]Purge cancelled.[/]")
            raise typer.Exit(0)
    now = time.time()
    count = 0
    for f in QUAR_DIR.iterdir():
        if f.is_file():
            age_days = (now - f.stat().st_ctime) / 86400
            if age_days > days:
                f.unlink()
                meta = f.with_suffix(f.suffix + ".meta")
                if meta.exists():
                    meta.unlink()
                count += 1
    console.print(f"[yellow]Purged {count} quarantined files older than {days} days.")
