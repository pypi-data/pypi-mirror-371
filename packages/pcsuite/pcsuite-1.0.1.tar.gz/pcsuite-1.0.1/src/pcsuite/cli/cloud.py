import typer
from rich.console import Console
from pcsuite.core.cloud_sync import sync_reports

app = typer.Typer(help="Cloud sync of reports")
console = Console()

@app.command()
def sync():
    """Sync all local reports to cloud folder."""
    ok = sync_reports()
    if ok:
        console.print("[green]Reports synced to cloud folder.")
    else:
        console.print("[red]Failed to sync reports.")
