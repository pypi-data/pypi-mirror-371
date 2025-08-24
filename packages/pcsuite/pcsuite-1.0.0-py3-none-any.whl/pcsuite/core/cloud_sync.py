import shutil
from pathlib import Path
import typer

CLOUD_DIR = Path.home() / "PCSuiteCloudReports"


def sync_reports(local_reports: Path = Path.cwd() / "reports"):
    CLOUD_DIR.mkdir(exist_ok=True)
    for f in local_reports.glob("*.json"):
        dest = CLOUD_DIR / f.name
        shutil.copy2(f, dest)
    return True
