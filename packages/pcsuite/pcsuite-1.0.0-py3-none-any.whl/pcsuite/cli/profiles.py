import typer
from rich.console import Console
from pcsuite.core import profiles
import json

app = typer.Typer(help="Manage cleanup profiles (saved options)")
console = Console()

@app.command()
def list():
    """List all saved profiles."""
    profs = profiles.load_profiles()
    for name, opts in profs.items():
        console.print(f"[cyan]{name}[/]: {json.dumps(opts)}")

@app.command()
def save(name: str, options: str = typer.Argument(..., help="Options as JSON string")):
    """Save a profile with given options (as JSON string)."""
    try:
        opts = json.loads(options)
    except Exception as e:
        console.print(f"[red]Invalid JSON:[/] {e}")
        raise typer.Exit(1)
    profiles.save_profile(name, opts)
    console.print(f"[green]Saved profile:[/] {name}")

@app.command()
def show(name: str):
    """Show a profile's options."""
    opts = profiles.get_profile(name)
    if not opts:
        console.print(f"[yellow]Profile not found:[/] {name}")
    else:
        console.print(json.dumps(opts, indent=2))

@app.command()
def delete(name: str):
    """Delete a profile."""
    profs = profiles.load_profiles()
    if name in profs:
        del profs[name]
        with open(profiles.PROFILES_PATH, "w", encoding="utf-8") as f:
            json.dump(profs, f, indent=2)
        console.print(f"[green]Deleted profile:[/] {name}")
    else:
        console.print(f"[yellow]Profile not found:[/] {name}")
