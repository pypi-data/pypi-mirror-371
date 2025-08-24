import typer
from rich.console import Console
from rich.table import Table
import subprocess
import socket

app = typer.Typer(help="Network diagnostics and info")
console = Console()

@app.command()
def ping(host: str = typer.Argument("8.8.8.8", help="Host to ping")):
    """Quick ping test."""
    result = subprocess.run(["ping", host, "-n", "4"], capture_output=True, text=True)
    console.print(result.stdout)

@app.command()
def speedtest():
    """Run a speed test (requires speedtest-cli)."""
    result = subprocess.run(["speedtest", "--simple"], capture_output=True, text=True)
    if result.returncode == 0:
        console.print(result.stdout)
    else:
        console.print("[red]speedtest-cli not found. Install with 'pip install speedtest-cli'.")

@app.command()
def connections():
    """List active network connections."""
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    table = Table(title="Active Connections")
    table.add_column("Proto")
    table.add_column("Local Address")
    table.add_column("Foreign Address")
    table.add_column("State")
    table.add_column("PID")
    for line in lines:
        parts = line.split()
        if len(parts) >= 5 and parts[0] in ("TCP", "UDP"):
            table.add_row(*parts[:5])
    console.print(table)
