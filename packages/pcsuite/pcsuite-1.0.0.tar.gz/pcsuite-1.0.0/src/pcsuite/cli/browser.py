import typer
from rich.console import Console
from rich.table import Table
import os
import shutil
from pathlib import Path

app = typer.Typer(help="Browser cache/cookie/session cleanup")
console = Console()

BROWSER_PATHS = {
    "chrome": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Cookies"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Sessions"),
    ],
    "edge": [
        os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\Cookies"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\Sessions"),
    ],
    "firefox": [
        os.path.expandvars(r"%APPDATA%\\Mozilla\\Firefox\\Profiles"),
    ],
}

@app.command()
def list():
    """List browser cache/cookie/session locations."""
    table = Table(title="Browser Data Locations")
    table.add_column("Browser")
    table.add_column("Path")
    for browser, paths in BROWSER_PATHS.items():
        for p in paths:
            table.add_row(browser, p)
    console.print(table)

@app.command()
def clean(browser: str = typer.Option("all", help="Browser to clean (chrome|edge|firefox|all)")):
    """Clean browser cache/cookie/session data."""
    targets = BROWSER_PATHS if browser == "all" else {browser: BROWSER_PATHS.get(browser, [])}
    cleaned = 0
    for b, paths in targets.items():
        for p in paths:
            pth = Path(p)
            if pth.exists():
                if pth.is_dir():
                    shutil.rmtree(pth, ignore_errors=True)
                    cleaned += 1
                elif pth.is_file():
                    pth.unlink(missing_ok=True)
                    cleaned += 1
    console.print(f"[green]Cleaned {cleaned} browser data locations.")
