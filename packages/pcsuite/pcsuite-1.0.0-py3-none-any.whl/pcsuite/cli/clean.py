
import sys
from pcsuite.core import fs
from pcsuite.core.elevation import is_admin, elevate_self
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from pcsuite.core import fs


app = typer.Typer(help="Cleaning tools")
console = Console()

def _cat_list(s: str) -> list[str]:
    return [c.strip() for c in s.split(",") if c.strip()]

@app.command()
def preview(
    category: str = typer.Option("temp,browser,dumps,do,recycle", help="Comma list"),
    min_age_days: int = typer.Option(0, help="Only include files older than N days"),
    min_size: int = typer.Option(0, help="Only include files >= this many bytes"),
    write_report: bool = typer.Option(True, help="Write preview report to reports/"),
    exclude_zero: bool = typer.Option(False, help="Exclude zero-byte files"),
    top: int = typer.Option(None, help="Limit to top N files"),
    sort: str = typer.Option("size", help="Sort by: size|name|age (default: size desc)"),
    only_ext: str = typer.Option(None, help="Only include files with these extensions (comma-separated, e.g. .log,.tmp)"),
    elevate: bool = typer.Option(
        False,
        help="If not admin, auto-elevate and re-run this command. (Hint: Use --elevate if you see 'Access is denied' or need admin rights.)"
    ),
):
    cats = _cat_list(category)

    # Elevation logic (same as run)
    if elevate and not is_admin():
        elevate_self(sys.argv[1:])
        return
    items = fs.enumerate_targets(
        cats,
        min_age_days=min_age_days if min_age_days > 0 else None,
        min_size=min_size if min_size > 0 else None,
    )
    if exclude_zero:
        items = [t for t in items if t.size > 0]
    filter_exts = None
    if only_ext:
        filter_exts = [e.strip().lower() for e in only_ext.split(",") if e.strip()]
        items = [t for t in items if any(t.path.lower().endswith(ext) for ext in filter_exts)]
    # De-dup by (path, category) while preserving order
    seen = set()
    items = [t for t in items if not ((t.path, t.category) in seen or seen.add((t.path, t.category)))]
    # Sort
    if sort == "size":
        items.sort(key=lambda t: t.size, reverse=True)
    elif sort == "name":
        items.sort(key=lambda t: t.path.lower())
    elif sort == "age":
        # Age sort not implemented; placeholder
        pass
    if top:
        items = items[:top]
    table = Table(title="Preview: Files to Clean")
    table.add_column("Category", style="cyan")
    table.add_column("Path")
    table.add_column("Size", justify="right")
    total = 0
    for t in items:
        table.add_row(t.category, t.path, f"{t.size:,}")
        total += t.size
    console.print(table)
    console.print(f"[bold]Total bytes[/]: {total:,}")
    if write_report:
        report = {
            "run_id": "preview-" + fs._new_run_id(),  # type: ignore
            "mode": "preview",
            "categories": cats,
            "min_age_days": min_age_days if min_age_days > 0 else None,
            "min_size": min_size if min_size > 0 else None,
            "total_bytes": total,
            "items": [t.__dict__ for t in items],
            "filters": {
                "category": category,
                "min_age_days": min_age_days,
                "min_size": min_size,
                "exclude_zero": exclude_zero,
                "top": top,
                "sort": sort,
                "only_ext": only_ext,
            },
        }
        path = fs.save_report(report)
        console.print(f"[green]Preview report:[/] {path}")

@app.command()
def run(
    category: str = typer.Option("temp,browser,dumps,do,recycle", help="Comma list"),
    mode: str = typer.Option("quarantine", help="quarantine|delete"),
    min_age_days: int = typer.Option(0, help="Only delete files older than N days"),
    min_size: int = typer.Option(0, help="Only delete files >= this many bytes"),
    from_report: Path = typer.Option(None, help="Use exact paths from a preview JSON"),
    dry_run: bool = typer.Option(False, help="Do not modify files; show what would happen"),
    retries: int = typer.Option(0, help="Retries per file on failure (e.g., locked)"),
    retry_delay_ms: int = typer.Option(150, help="Delay between retries (ms)"),
    delete_mode: str = typer.Option("hard", help="Deletion method: hard | recycle"),
    restore_point: bool = typer.Option(False, "--restore-point/--no-restore-point", help="Create a Windows restore point before changes"),
    elevate: bool = typer.Option(
        False,
        help="If not admin, auto-elevate and re-run this command. (Hint: Use --elevate if you see 'Access is denied' or need admin rights.)"
    ),
    on_reboot_fallback: bool = typer.Option(
        False,
        "--on-reboot-fallback/--no-on-reboot-fallback",
        help="If a file is in use, schedule a safe delete at next reboot."
    ),
    ignore_missing: bool = typer.Option(
        True, "--ignore-missing/--no-ignore-missing",
        help="Treat missing files as skipped instead of errors."
    ),
    progress: bool = typer.Option(
        True, "--progress/--no-progress",
        help="Show a live progress bar during cleanup."
    ),
    exclude_zero: bool = typer.Option(False, help="Exclude zero-byte files"),
    top: int = typer.Option(None, help="Limit to top N files"),
    sort: str = typer.Option("size", help="Sort by: size|name|age (default: size desc)"),
    only_ext: str = typer.Option(None, help="Only include files with these extensions (comma-separated, e.g. .log,.tmp)"),
):
    # If user asked to elevate, do it before any work
    if elevate and not is_admin() and not dry_run:
        # Relaunch the exact same subcommand with admin rights
        elevate_self(sys.argv[1:])   # re-run "pcsuite clean run …" under UAC
        return
    
    def _cats(s: str) -> list[str]:
        return [c.strip() for c in s.split(",") if c.strip()]

    cats = _cats(category)
    explicit = None
    if from_report:
        try:
            data = fs.load_report(from_report)
            # Collect all unique paths from items[].path, items[].from, and legacy files
            paths = set()
            for it in data.get("items", []):
                if "path" in it:
                    paths.add(it["path"])
                if "from" in it:
                    paths.add(it["from"])
            for f in data.get("files", []):
                paths.add(f)
            explicit = list(paths) if paths else None
        except Exception as e:
            console.print(f"[red]Failed to load report:[/] {e}")
            raise typer.Exit(code=2)

    # If not from-report, show a quick progress bar based on enumerated items

    items_for_progress = None
    filter_exts = None
    if only_ext:
        filter_exts = [e.strip().lower() for e in only_ext.split(",") if e.strip()]

    if not from_report:
        items_for_progress = fs.enumerate_targets(
            cats, min_age_days=min_age_days or None, min_size=min_size or None
        )
        # Apply exclude_zero
        if exclude_zero:
            items_for_progress = [t for t in items_for_progress if t.size > 0]
        # Apply only_ext
        if filter_exts:
            items_for_progress = [t for t in items_for_progress if any(t.path.lower().endswith(ext) for ext in filter_exts)]
        # Sort
        if sort == "size":
            items_for_progress.sort(key=lambda t: t.size, reverse=True)
        elif sort == "name":
            items_for_progress.sort(key=lambda t: t.path.lower())
        elif sort == "age":
            # Age sort not implemented; placeholder
            pass
        # Top N
        if top:
            items_for_progress = items_for_progress[:top]
        total = len(items_for_progress)
        if total == 0:
            console.print("[yellow]Nothing to do with current filters.[/]")
    else:
        total = len(explicit or [])

    # Progress line
    console.print(f"[blue]Processing {total} files...[/]")

    from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
    progress_hook = None
    total_files = total if items_for_progress is not None else None

    if progress and total_files:
        prog = Progress(
            TextColumn("[cyan]Cleaning[/]"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TextColumn(" • M:{task.fields[moved]} D:{task.fields[deleted]} S:{task.fields[skipped]} E:{task.fields[errors]}"),
            transient=True,
        )
        task = prog.add_task("clean", total=total_files, moved=0, deleted=0, skipped=0, errors=0)

        def _hook(ev: dict):
            s = ev.get("stats", {})
            prog.update(task, advance=1,
                        moved=s.get("moved", 0),
                        deleted=s.get("deleted", 0),
                        skipped=s.get("skipped", 0),
                        errors=s.get("errors", 0))

        progress_hook = _hook
        prog.__enter__()


    try:
        # If not from_report, pass explicit_paths from filtered items_for_progress
        if not from_report:
            explicit_paths = [t.path for t in items_for_progress]
        else:
            explicit_paths = explicit
        report = fs.execute_cleanup(
            cats,
            mode=mode,
            min_age_days=(None if from_report else (min_age_days or None)),
            min_size=(None if from_report else (min_size or None)),
            explicit_paths=explicit_paths,
            dry_run=dry_run,
            retries=retries,
            retry_delay_ms=retry_delay_ms,
            delete_mode=delete_mode,
            restore_point=restore_point,
            on_reboot_fallback=on_reboot_fallback,
            ignore_missing=ignore_missing,
            progress_hook=progress_hook,
        )
    finally:
        if progress and total_files:
            prog.__exit__(None, None, None)

    # Store filters in report
    report["filters"] = {
        "category": category,
        "min_age_days": min_age_days,
        "min_size": min_size,
        "exclude_zero": exclude_zero,
        "top": top,
        "sort": sort,
        "only_ext": only_ext,
    }
    path = fs.save_report(report)

    stats = report.get("stats", {})
    bytes_h = fs._human(int(stats.get("bytes_reclaimed", 0)))

    # Pretty summary
    action = "Would reclaim" if dry_run else "Reclaimed"
    console.print(
        f"[bold green]Cleanup complete.[/] "
        f"{stats.get('moved', 0)} moved, {stats.get('deleted', 0)} deleted, "
        f"{stats.get('skipped', 0)} skipped, {stats.get('errors', 0)} errors. "
        f"{action}: {bytes_h}. Report: {path}"
    )
    if report.get("restore_point") is not None:
        rp = report["restore_point"]
        msg = "[yellow]Restore point:[/] "
        if not rp.get("attempted"):
            msg += "Not attempted"
        elif rp.get("ok"):
            msg += "Created successfully"
        else:
            msg += f"Failed ({rp.get('error','unknown error')})"
        console.print(msg)
