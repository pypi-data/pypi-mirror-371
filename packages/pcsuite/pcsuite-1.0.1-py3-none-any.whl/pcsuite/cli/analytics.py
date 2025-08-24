import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import glob
import datetime
import csv

app = typer.Typer(help="Analytics: cumulative stats and trend reports")
console = Console()
REPORTS_DIR = Path.cwd() / "reports"

@app.command()
def export(path: Path = typer.Argument("analytics_export.csv", help="CSV file to write")):
    """Export per-run analytics data to CSV for external analysis."""
    if not REPORTS_DIR.exists():
        console.print("[yellow]No reports directory found.[/]")
        raise typer.Exit(1)
    files = list(REPORTS_DIR.glob("*.json"))
    if not files:
        console.print("[yellow]No report files found.[/]")
        raise typer.Exit(1)
    rows = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            when = data.get("when", "?")
            stats = data.get("stats", {})
            bytes_reclaimed = stats.get("bytes_reclaimed", 0)
            files_examined = stats.get("examined", 0)
            # Find top category for this run
            cat_bytes = {}
            for item in data.get("items", []):
                cat = item.get("category", "?")
                cat_bytes.setdefault(cat, 0)
                cat_bytes[cat] += int(item.get("size", 0))
            top_cat = max(cat_bytes.items(), key=lambda x: x[1])[0] if cat_bytes else "?"
            rows.append({
                "date": when,
                "bytes_reclaimed": bytes_reclaimed,
                "files_examined": files_examined,
                "top_category": top_cat,
            })
        except Exception:
            continue
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["date", "bytes_reclaimed", "files_examined", "top_category"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    console.print(f"[green]Exported analytics to:[/] {path}")

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import glob
import datetime

app = typer.Typer(help="Analytics: cumulative stats and trend reports")
console = Console()
REPORTS_DIR = Path.cwd() / "reports"

@app.command()
def recommend():
    """Suggest cleaning actions based on report history."""
    if not REPORTS_DIR.exists():
        console.print("[yellow]No reports directory found.[/]")
        raise typer.Exit(1)
    files = list(REPORTS_DIR.glob("*.json"))
    if not files:
        console.print("[yellow]No report files found.[/]")
        raise typer.Exit(1)
    cat_bytes = {}
    cat_runs = {}
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            for item in data.get("items", []):
                cat = item.get("category", "?")
                cat_bytes.setdefault(cat, 0)
                cat_bytes[cat] += int(item.get("size", 0))
                cat_runs.setdefault(cat, 0)
                cat_runs[cat] += 1
        except Exception:
            continue
    if not cat_bytes:
        console.print("[yellow]No actionable data found in reports.[/]")
        return
    # Top categories by bytes
    top_cats = sorted(cat_bytes.items(), key=lambda x: x[1], reverse=True)
    console.print("[bold]Top categories by junk accumulation:[/]")
    for cat, b in top_cats[:5]:
        console.print(f"  [cyan]{cat}[/]: {b:,} bytes")
    # Categories with fewest runs (rarely cleaned)
    fewest = sorted(cat_runs.items(), key=lambda x: x[1])
    console.print("\n[bold]Categories rarely cleaned:[/]")
    for cat, n in fewest[:3]:
        console.print(f"  [magenta]{cat}[/]: cleaned {n} times")
    # Suggest cleaning frequency
    if top_cats:
        console.print("\n[bold]Recommendation:[/]")
        cat, b = top_cats[0]
        if b > 100*1024*1024:
            console.print(f"Consider cleaning [cyan]{cat}[/] more frequently (over 100MB accumulated).")
        else:
            console.print(f"Your cleaning schedule looks good. No urgent action needed.")

@app.command()
def stats():
    """Show cumulative stats: total space reclaimed, files handled over time."""
    total_bytes = 0
    total_files = 0
    for f in glob.glob(str(REPORTS_DIR / "*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                stats = data.get("stats", {})
                total_bytes += stats.get("bytes_reclaimed", 0)
                total_files += stats.get("examined", 0)
        except Exception:
            continue
    console.print(f"[bold]Total space reclaimed:[/] {total_bytes:,} bytes")
    console.print(f"[bold]Total files handled:[/] {total_files:,}")

@app.command()
def trends():
    """Show trend report: space reclaimed per day/week/month."""
    trends = {}
    for f in glob.glob(str(REPORTS_DIR / "*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                when = data.get("when")
                stats = data.get("stats", {})
                if when and stats.get("bytes_reclaimed"):
                    date = when.split("T")[0]
                    trends.setdefault(date, 0)
                    trends[date] += stats["bytes_reclaimed"]
        except Exception:
            continue
    table = Table(title="Space Reclaimed by Date")
    table.add_column("Date")
    table.add_column("Bytes Reclaimed", justify="right")
    for date in sorted(trends.keys()):
        table.add_row(date, f"{trends[date]:,}")
    console.print(table)
