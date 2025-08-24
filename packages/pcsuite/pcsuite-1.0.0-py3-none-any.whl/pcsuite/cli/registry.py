import typer
from rich.console import Console
from rich.table import Table
import winreg

app = typer.Typer(help="Registry temp/leftover entries cleanup")
console = Console()

# Example: common temp/leftover keys (expand as needed)
REG_TEMP_KEYS = [
    (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU"),
    (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSavePidlMRU"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Installer\\Folders"),
]

@app.command()
def list():
    """List known temp/leftover registry keys."""
    table = Table(title="Registry Temp/Leftover Keys")
    table.add_column("Hive")
    table.add_column("Path")
    for hive, path in REG_TEMP_KEYS:
        hname = "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM"
        table.add_row(hname, path)
    console.print(table)

@app.command()
def clean():
    """Delete values from known temp/leftover registry keys."""
    cleaned = 0
    for hive, path in REG_TEMP_KEYS:
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                # Enumerate and delete all values
                i = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(key, 0)
                        winreg.DeleteValue(key, name)
                        cleaned += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
        except PermissionError:
            console.print(f"[red]Permission denied for {path}. Try running as administrator.")
    console.print(f"[green]Cleaned {cleaned} registry values.")
