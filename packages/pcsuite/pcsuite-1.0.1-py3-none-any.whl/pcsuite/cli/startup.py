
import typer
from rich.console import Console
from rich.table import Table
import winreg
import os

app = typer.Typer(help="Startup program audit and management")
console = Console()
STARTUP_LOCATIONS = [
	(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
	(winreg.HKEY_LOCAL_MACHINE, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
]

@app.command()
def list():
	"""List all startup programs (user + system)."""
	table = Table(title="Startup Programs")
	table.add_column("Location")
	table.add_column("Name")
	table.add_column("Command")
	for hive, path in STARTUP_LOCATIONS:
		try:
			with winreg.OpenKey(hive, path) as key:
				i = 0
				while True:
					try:
						name, value, _ = winreg.EnumValue(key, i)
						loc = "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM"
						table.add_row(f"{loc}\\{path}", name, value)
						i += 1
					except OSError:
						break
		except FileNotFoundError:
			continue
	console.print(table)

@app.command()
def disable(name: str, user: bool = typer.Option(True, help="Disable for current user (else system-wide)")):
	"""Disable a startup program by name."""
	hive, path = (winreg.HKEY_CURRENT_USER, STARTUP_LOCATIONS[0][1]) if user else (winreg.HKEY_LOCAL_MACHINE, STARTUP_LOCATIONS[1][1])
	try:
		with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
			winreg.DeleteValue(key, name)
		console.print(f"[green]Disabled:[/] {name}")
	except FileNotFoundError:
		console.print(f"[yellow]Not found:[/] {name}")
	except PermissionError:
		console.print(f"[red]Permission denied. Try running as administrator.")
import typer
app = typer.Typer()
