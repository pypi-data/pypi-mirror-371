from __future__ import annotations
import os
import sys
import ctypes
import subprocess
from typing import Sequence

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    except Exception:
        return False

def _quote(a: str) -> str:
    # Conservative quoting for PowerShell/CMD handoff
    if " " in a or '"' in a:
        return f'"{a.replace("\"", "\\\"")}"'
    return a

def elevate_self(argv: Sequence[str] | None = None) -> None:
    """
    Relaunch this process with UAC elevation (Run as Administrator).
    Returns only if elevation fails; on success, current process exits.
    """
    if argv is None:
        argv = sys.argv

    # Prevent infinite loops if we’re already elevated
    if os.environ.get("PCS_ELEVATED") == "1":
        return

    # Build the exact command line again
    exe = sys.executable  # the venv Python
    cmdline = " ".join(_quote(a) for a in [exe, "-m"] + list(argv[0:]))

    # Use PowerShell Start-Process -Verb RunAs to preserve PATH/venv
    argstr = '-m ' + ' '.join(argv)
    ps_cmd = [
        "powershell", "-NoProfile", "-Command",
        f"$env:PCS_ELEVATED='1'; Start-Process -Verb RunAs -FilePath { _quote(exe) } -ArgumentList { _quote(argstr) }"
    ]
    try:
        subprocess.check_call(ps_cmd)
        # If elevation succeeds, exit current (non-admin) process.
        os._exit(0)
    except subprocess.CalledProcessError:
        # Bubble up; caller can decide what to do.
        pass
