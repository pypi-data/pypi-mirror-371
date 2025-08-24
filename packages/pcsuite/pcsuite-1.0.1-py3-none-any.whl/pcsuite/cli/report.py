import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

app = typer.Typer(help="Report inspection and summary tools")
console = Console()

@app.command()
def inspect(file: Path):
    """Show a summary of a cleanup or preview report JSON file."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load report:[/] {e}")
        raise typer.Exit(code=2)

    console.print(f"[bold]Report:[/] {file}")
    console.print(f"[cyan]Run ID:[/] {data.get('run_id','?')}")
    console.print(f"[cyan]Mode:[/] {data.get('mode','?')}")
    filters = data.get('filters') or {}
    if filters:
        console.print("[cyan]Filters:[/]")
        for k, v in filters.items():
            console.print(f"  [magenta]{k}[/]: {v}")
    stats = data.get('stats') or {}
    if stats:
        console.print("[cyan]Stats:[/]")
        for k, v in stats.items():
            console.print(f"  [magenta]{k}[/]: {v}")
    items = data.get('items', [])
    if items:
        table = Table(title="Sample of affected files", show_lines=True)
        table.add_column("Path")
        table.add_column("Category")
        table.add_column("Size", justify="right")
        table.add_column("Status", justify="right")
        for it in items[:10]:
            table.add_row(str(it.get('from') or it.get('path','?')), str(it.get('category','?')), str(it.get('size','?')), str(it.get('status','?')))
        console.print(table)
        if len(items) > 10:
            console.print(f"[dim]...and {len(items)-10} more files.[/]")
    else:
        console.print("[yellow]No affected files in this report.[/]")
