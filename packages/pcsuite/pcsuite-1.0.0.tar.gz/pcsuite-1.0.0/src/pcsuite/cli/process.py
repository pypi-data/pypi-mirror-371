
import typer
from rich.console import Console
from rich.table import Table
import psutil
import time

app = typer.Typer(help="RAM/process monitor and auto-kill rules")
console = Console()

@app.command()
def list():
	"""List all running processes with RAM usage."""
	table = Table(title="Processes")
	table.add_column("PID")
	table.add_column("Name")
	table.add_column("RAM (MB)", justify="right")
	for p in psutil.process_iter(['pid', 'name', 'memory_info']):
		try:
			mem = p.info['memory_info'].rss / (1024*1024)
			table.add_row(str(p.info['pid']), p.info['name'], f"{mem:.1f}")
		except Exception:
			continue
	console.print(table)

@app.command()
def kill_ram(threshold: float = typer.Argument(..., help="RAM usage MB threshold")):
	"""Kill processes using more than threshold MB RAM."""
	killed = 0
	for p in psutil.process_iter(['pid', 'name', 'memory_info']):
		try:
			mem = p.info['memory_info'].rss / (1024*1024)
			if mem > threshold:
				p.kill()
				console.print(f"[red]Killed:[/] {p.info['name']} (PID {p.info['pid']}) using {mem:.1f} MB")
				killed += 1
		except Exception:
			continue
	if killed == 0:
		console.print("[green]No processes exceeded threshold.")
	else:
		console.print(f"[yellow]Total killed: {killed}")
app = typer.Typer()
import typer
app = typer.Typer()
