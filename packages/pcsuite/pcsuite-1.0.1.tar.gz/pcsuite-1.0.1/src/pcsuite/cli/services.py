
import typer
import subprocess
from rich.table import Table
from rich.console import Console

app = typer.Typer(help="Service management tools")
console = Console()

@app.command()
def list():
	"""List all running services."""
	result = subprocess.run(["sc", "query", "state= all"], capture_output=True, text=True)
	lines = result.stdout.splitlines()
	table = Table(title="Windows Services")
	table.add_column("Service Name")
	table.add_column("Display Name")
	table.add_column("State")
	name, display, state = None, None, None
	for line in lines:
		if line.strip().startswith("SERVICE_NAME:"):
			name = line.split(":", 1)[1].strip()
		elif line.strip().startswith("DISPLAY_NAME:"):
			display = line.split(":", 1)[1].strip()
		elif line.strip().startswith("STATE"):
			state = line.split(":", 1)[1].split()[0].strip()
			if name and display and state:
				table.add_row(name, display, state)
				name, display, state = None, None, None
	console.print(table)

@app.command()
def stop(name: str):
	"""Stop a service by name."""
	result = subprocess.run(["sc", "stop", name], capture_output=True, text=True)
	if "SUCCESS" in result.stdout:
		console.print(f"[green]Stopped:[/] {name}")
	else:
		console.print(f"[red]Failed to stop:[/] {name}\n{result.stdout}")

@app.command()
def disable(name: str):
	"""Disable a service by name."""
	result = subprocess.run(["sc", "config", name, "start= disabled"], capture_output=True, text=True)
	if "SUCCESS" in result.stdout:
		console.print(f"[green]Disabled:[/] {name}")
	else:
		console.print(f"[red]Failed to disable:[/] {name}\n{result.stdout}")
import typer
app = typer.Typer()
