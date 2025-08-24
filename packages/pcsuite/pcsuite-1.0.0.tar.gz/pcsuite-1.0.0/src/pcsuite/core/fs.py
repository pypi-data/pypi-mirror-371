
from __future__ import annotations
from pathlib import Path
import errno
import ctypes
import os

MOVEFILE_DELAY_UNTIL_REBOOT = 0x00000004

def _win_long_path(p: str) -> str:
	# Add \\?\ prefix to support long paths and bypass normalization issues
	if p.startswith('\\\\?\\'):
		return p
	if p.startswith('\\\\'):
		return '\\?\\UNC\\' + p[2:]
	return '\\?\\' + p

def schedule_delete_on_reboot(path: Path) -> tuple[bool, str | None]:
	"""
	Best-effort schedule a delete at next reboot via MoveFileExW.
	Returns (ok, err) where err is a friendly message if ok == False.
	"""
	try:
		MoveFileExW = ctypes.windll.kernel32.MoveFileExW  # type: ignore[attr-defined]
		MoveFileExW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
		MoveFileExW.restype = ctypes.c_int
		src = str(path)
		print(f"[DEBUG] schedule_delete_on_reboot: src={src!r}")
		ok = MoveFileExW(src, None, MOVEFILE_DELAY_UNTIL_REBOOT)
		if ok:
			return True, None
		# get the real failure code/message
		code = ctypes.GetLastError()
		buf = ctypes.create_unicode_buffer(512)
		ctypes.windll.kernel32.FormatMessageW(
			0x00001000,  # FORMAT_MESSAGE_FROM_SYSTEM
			None,
			code,
			0,
			buf,
			len(buf),
			None,
		)
		return False, f"MoveFileExW failed with code {code}: {buf.value.strip()} | src={src!r}"
	except Exception as e:
		return False, f"Exception: {e} | src={src!r}"

MOVEFILE_DELAY_UNTIL_REBOOT = 0x00000004


def _is_in_use(exc: BaseException) -> bool:
	"""Return True if exception looks like a locked/in-use file error."""
	msg = str(exc).lower()
	# Common signals: WinError 32, PermissionError on Windows, typical phrasings
	if isinstance(exc, PermissionError):
		return True
	if isinstance(exc, OSError):
		if getattr(exc, "winerror", None) == 32:
			return True
		if exc.errno in (errno.EACCES, errno.EBUSY):
			return True
	needles = [
		"being used by", "in use",
		"process cannot access the file",
		"access is denied",
		"file is open in",
		"the action can't be completed because the file is open",
	]
	return any(n in msg for n in needles)


def save_report(report: Dict[str, Any]) -> Path:
	return _write_report(report["run_id"], report)

from pathlib import Path
import json
import sys, subprocess
from send2trash import send2trash
from typing import Optional, List, Dict, Any, Callable

def load_report(path: Path) -> dict:
	"""Load a JSON report written by save_report()."""
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional
import os, json, time, glob, shutil, uuid, subprocess
import yaml

@dataclass
class Target:
	path: str
	size: int
	category: str

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
REPORTS_DIR = Path.cwd() / "reports"
QUAR_DIR = Path.cwd() / "Quarantine"

def _load_yaml(fname: str) -> Dict[str, Any]:
	with open(DATA_DIR / fname, "r", encoding="utf-8") as f:
		return yaml.safe_load(f) or {}

def _expand(p: str) -> str:
	p = os.path.expandvars(p)
	return p.replace("/", "\\")  # Windows-friendly

def _glob_paths(patterns: Iterable[str]) -> List[Path]:
	paths: List[Path] = []
	for pat in patterns:
		pat = _expand(pat)
		# glob on Windows is case-insensitive-ish; still normalize
		paths.extend(Path(p) for p in glob.glob(pat, recursive=True))
	return paths

def _excluded(p: Path, exclusions: List[Path]) -> bool:
	# simple prefix check; normalize
	sp = str(p.resolve()) if p.exists() else str(p)
	for e in exclusions:
		if sp.lower().startswith(str(e).lower()):
			return True
	return False

def _ensure_dirs() -> None:
	REPORTS_DIR.mkdir(parents=True, exist_ok=True)
	QUAR_DIR.mkdir(parents=True, exist_ok=True)

def _new_run_id() -> str:
	return time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]

def _write_report(run_id: str, report: Dict[str, Any]) -> Path:
	_ensure_dirs()
	out = REPORTS_DIR / f"{run_id}.json"
	with open(out, "w", encoding="utf-8") as f:
		json.dump(report, f, indent=2)
	return out

def _create_restore_point(description: str) -> None:
	"""
	Best-effort System Restore Point via PowerShell/WMI.
	Requires admin; non-fatal if it fails (we log in report).
	"""
	ps = [
		"powershell",
		"-NoProfile",
		"-ExecutionPolicy", "Bypass",
		"-Command",
		(
			"$desc = '{}'; "
			"try { "
			"Checkpoint-Computer -Description $desc -RestorePointType 'MODIFY_SETTINGS' "
			"} catch { "
			"exit 2 "
			"}"
		).format(description.replace("'", "''"))
	]
	try:
		subprocess.run(ps, check=True, capture_output=True)
	except subprocess.CalledProcessError:
		# swallow — caller will record failure in report
		pass

def create_restore_point(run_id: str) -> dict:
    """Best-effort Windows System Restore point. Never raises."""
    info = {"attempted": False, "ok": False, "error": None}
    if sys.platform != "win32":
        return info
    info["attempted"] = True
    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f'Checkpoint-Computer -Description "PCSuite {run_id}" -RestorePointType "MODIFY_SETTINGS"'
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        info["ok"] = True
    except Exception as e:
        info["error"] = str(e)
    return info

def _file_age_days(p: Path) -> float:
	try:
		mtime = p.stat().st_mtime
		return (time.time() - mtime) / 86400.0
	except OSError:
		return 0.0

def load_catalog() -> tuple[Dict[str, Any], List[Path]]:
	sig = _load_yaml("signatures.yml").get("categories", {})
	excl_raw = _load_yaml("exclusions.yml")
	if isinstance(excl_raw, dict):
		excl = excl_raw.get("paths", [])
	elif isinstance(excl_raw, list):
		excl = excl_raw
	else:
		excl = []
	exclusions = [Path(_expand(p)) for p in excl]
	return sig, exclusions

def enumerate_targets(categories: List[str], min_age_days: int | None = None, min_size: int | None = None) -> List[Target]:
	sig, exclusions = load_catalog()
	targets: List[Target] = []
	for cat in categories:
		entry = sig.get(cat)
		if not entry:
			continue
		if entry.get("special") == "recycle_bin":
			# handled by dedicated routine; skip listing files here
			continue
		globs = entry.get("globs", [])
		for p in _glob_paths(globs):
			try:
				if _excluded(p, exclusions):
					continue
				if p.is_file():
					if min_age_days is not None and _file_age_days(p) < float(min_age_days):
						continue
					if min_size is not None and p.stat().st_size < min_size:
						continue
					targets.append(Target(str(p), p.stat().st_size, cat))
			except OSError:
				# ignore unreadable paths
				continue
	return targets

def _recycle_bin_summary() -> Dict[str, Any]:
	# Placeholder: enumerate size/count with Shell API (to do in next pass).
	return {"count": 0, "bytes": 0}

def _purge_recycle_bin() -> Dict[str, Any]:
	"""
	Empty Recycle Bin using Shell32 SHEmptyRecycleBin via PowerShell.
	"""
	ps = [
		"powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
		r"""
Add-Type -AssemblyName Microsoft.VisualBasic
$shell = New-Object -ComObject Shell.Application
# Flags: 0x0007 = no confirm, no progress UI, no sound
$r = (New-Object -ComObject Shell.Application).NameSpace(0xA)
# Fallback to SHEmptyRecycleBin if needed
$signature = @'
using System;
using System.Runtime.InteropServices;
public class Recycle {
  [DllImport("Shell32.dll", CharSet=CharSet.Unicode)]
  public static extern int SHEmptyRecycleBin(IntPtr hWnd, string pszRootPath, uint dwFlags);
}
'@
Add-Type -TypeDefinition $signature -ErrorAction SilentlyContinue
[Recycle]::SHEmptyRecycleBin([IntPtr]::Zero, null, 0x0007) | Out-Null
""",
	]
	try:
		subprocess.run(ps, check=True, capture_output=True)
		return {"ok": True}
	except subprocess.CalledProcessError as e:
		return {"ok": False, "error": str(e)}

def execute_cleanup(
    categories: List[str],
    mode: str = "quarantine",
    min_age_days: Optional[int] = None,
    min_size: Optional[int] = None,
    explicit_paths: Optional[List[str]] = None,
    dry_run: bool = False,
    retries: int = 0,
    retry_delay_ms: int = 150,
    delete_mode: str = "hard",      # "hard" or "recycle"
    restore_point: bool = False,    # create a restore point before changes
    on_reboot_fallback: bool = False,
    ignore_missing: bool = True,
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:

	"""
	If explicit_paths is provided, we act on that exact list (for 'run --from-report').
	Otherwise we re-enumerate with given filters.

	dry_run=True -> no file system changes, but we still compute stats.
	retries -> number of extra attempts per file if an operation fails (e.g., locked). Simple sleep-retry.
	"""
	run_id = _new_run_id()
	report: Dict[str, Any] = {
		"run_id": run_id,
		"when": time.strftime("%Y-%m-%dT%H:%M:%S"),
		"mode": mode,
		"categories": categories,
		"delete_mode": delete_mode,
		"on_reboot_fallback": on_reboot_fallback if 'on_reboot_fallback' in locals() else False,
		"min_age_days": min_age_days,
		"min_size": min_size,
		"dry_run": dry_run,
		"retries": retries,
		"retry_delay_ms": retry_delay_ms,
		"stats": {
			"examined": 0,
			"moved": 0,
			"deleted": 0,
			"skipped": 0,
			"errors": 0,
			"pending_reboot": 0,
			"bytes_reclaimed": 0
		},
		"items": [],
		"errors": [],
		"skipped": [],
	}
	stats = report["stats"]


	if restore_point and not dry_run:
		report["restore_point"] = create_restore_point(run_id)


	# Build target list
	if explicit_paths:
		targets: List[Target] = []
		for p in explicit_paths:
			try:
				pp = Path(p)
				if pp.is_file():
					st = pp.stat()
					targets.append(Target(str(pp), st.st_size, "unknown"))
			except OSError:
				pass
	else:
		targets = enumerate_targets(categories, min_age_days=min_age_days, min_size=min_size)

	report["stats"]["examined"] = len(targets)

	# Prepare quarantine dir if needed
	quar_dir = None
	if mode == "quarantine":
		quar_dir = QUAR_DIR / run_id
		if not dry_run:
			quar_dir.mkdir(parents=True, exist_ok=True)

	# Simple retry helper
	def _attempt(fn, *args, **kwargs):
		tries = 1 + max(0, int(retries))
		delay = max(0, int(retry_delay_ms)) / 1000.0
		last_exc = None
		for _ in range(tries):
			try:
				return fn(*args, **kwargs)
			except Exception as e:  # noqa: BLE001 (simple tool)
				last_exc = e
				if delay:
					time.sleep(delay)
		if last_exc:
			raise last_exc

	for t in targets:
		p = Path(t.path)
		cat = t.category
		size = t.size
		try:
			if dry_run:
				report["items"].append({"from": str(p), "size": size, "category": cat, "dry_run": True})
				stats["bytes_reclaimed"] += size
				status = "ok"
			else:
				if not p.exists() or not p.is_file():
					raise FileNotFoundError()
				if mode == "quarantine":
					import hashlib, json
					assert quar_dir is not None
					dst = quar_dir / p.name
					counter = 1
					while dst.exists():
						dst = dst.with_name(f"{dst.stem}_{counter}{dst.suffix}")
						counter += 1
					# Compute SHA256 hash before moving
					sha256 = None
					try:
						h = hashlib.sha256()
						with open(p, "rb") as fp:
							while chunk := fp.read(8192):
								h.update(chunk)
						sha256 = h.hexdigest()
					except Exception:
						pass
					try:
						_attempt(p.replace, dst)
					except OSError as move_exc:
						# Handle cross-drive move (WinError 17)
						if getattr(move_exc, "winerror", None) == 17 or (isinstance(move_exc, OSError) and move_exc.errno == 18):
							import shutil
							try:
								_attempt(shutil.copy2, str(p), str(dst))
								_attempt(p.unlink, missing_ok=True)
							except Exception as copy_exc:
								raise copy_exc from move_exc
						else:
							raise
					# Write metadata JSON
					meta = dst.with_suffix(dst.suffix + ".meta.json")
					meta_data = {"original_path": str(p), "sha256": sha256}
					try:
						with open(meta, "w", encoding="utf-8") as mf:
							json.dump(meta_data, mf)
					except Exception:
						pass
					stats["moved"] += 1
					status = "moved"
				else:
					if delete_mode == "recycle":
						_attempt(send2trash, str(p))
					else:
						_attempt(p.unlink, missing_ok=True)
					stats["deleted"] += 1
					status = "deleted"
				stats["bytes_reclaimed"] += size
				report["items"].append({"from": str(p), "category": cat, "size": size, "status": status})
		except FileNotFoundError:
			if ignore_missing:
				stats["skipped"] += 1
				report["items"].append({"from": str(p), "category": cat, "size": size, "status": "skipped", "reason": "missing"})
			else:
				stats["errors"] += 1
				report["items"].append({"from": str(p), "category": cat, "size": size, "status": "error", "error": "missing"})
		except Exception as e:
			locked = _is_in_use(e)
			if on_reboot_fallback and locked:
				ok, err = schedule_delete_on_reboot(p)
				if ok:
					stats["pending_reboot"] += 1
					report["items"].append({
						"from": str(p), "category": cat, "size": size,
						"status": "pending_reboot", "pending_reboot": True
					})
				else:
					stats["errors"] += 1
					report["items"].append({
						"from": str(p), "category": cat, "size": size,
						"status": "error",
						"error": f"on_reboot_schedule_failed: {err}",
						"exc_type": e.__class__.__name__
					})
			else:
				stats["errors"] += 1
				report["items"].append({
					"from": str(p), "category": cat, "size": size,
					"status": "error", "error": str(e), "exc_type": e.__class__.__name__
				})
		finally:
			stats["examined"] += 1
			if progress_hook:
				progress_hook({"event": "tick", "path": str(p), "stats": stats})
	return report

def save_report(report: Dict[str, Any]) -> Path:
	return _write_report(report["run_id"], report)

def _human(n: int) -> str:
    # Human-readable bytes (e.g., 1.2 MB)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != 'B' else f"{n} B"
        n /= 1024
    return f"{n:.1f} PB"
