
import typer
import subprocess
import sys
from rich.console import Console

app = typer.Typer(help="Scheduled cleanups (Windows Task Scheduler integration)")
console = Console()

@app.command()
def create(profile: str = typer.Argument(..., help="Profile name (e.g. weekly, monthly)"), when: str = typer.Option("weekly", help="Trigger: daily, weekly, monthly")):
	"""Create a scheduled cleanup task using Windows Task Scheduler."""
	task_name = f"PCSuite_{profile}"
	script = sys.executable + " -m pcsuite clean run --profile " + profile
	if when == "daily":
		schedule = "/SC DAILY"
	elif when == "monthly":
		schedule = "/SC MONTHLY"
	else:
		schedule = "/SC WEEKLY"
	cmd = f'schtasks /Create /TN {task_name} {schedule} /TR "{script}" /RL HIGHEST /F'
	result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
	if result.returncode == 0:
		console.print(f"[green]Scheduled task created:[/] {task_name}")
	else:
		console.print(f"[red]Failed to create task:[/] {result.stdout}\n{result.stderr}")

@app.command()
def list():
	"""List all PCSuite scheduled tasks."""
	result = subprocess.run('schtasks /Query /FO LIST /V', shell=True, capture_output=True, text=True)
	for line in result.stdout.splitlines():
		if "PCSuite_" in line:
			console.print(line)

@app.command()
def delete(profile: str = typer.Argument(..., help="Profile name")):
	"""Delete a scheduled cleanup task."""
	task_name = f"PCSuite_{profile}"
	result = subprocess.run(f'schtasks /Delete /TN {task_name} /F', shell=True, capture_output=True, text=True)
	if result.returncode == 0:
		console.print(f"[green]Deleted scheduled task:[/] {task_name}")
	else:
		console.print(f"[red]Failed to delete task:[/] {result.stdout}\n{result.stderr}")

