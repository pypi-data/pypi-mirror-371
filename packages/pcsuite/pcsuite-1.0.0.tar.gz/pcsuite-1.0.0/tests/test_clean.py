# tests/test_clean.py
from pathlib import Path
from typer.testing import CliRunner

from pcsuite.cli.clean import app as clean_app
from pcsuite.core import fs

runner = CliRunner()


def test_preview_filters(monkeypatch, tmp_path):
    # Fake targets (include zeros & duplicates to exercise filters)
    fake_targets = [
        fs.Target(path="C:/Temp/a.tmp", size=0, category="temp"),
        fs.Target(path="C:/Temp/b.tmp", size=500, category="temp"),
        fs.Target(path="C:/Temp/c.tmp", size=1500, category="temp"),
        fs.Target(path="C:/Temp/d.tmp", size=2500, category="temp"),
    ]

    # enumerate_targets signature: (categories, min_age_days=None, min_size=None)
    def fake_enumerate_targets(categories, min_age_days=None, min_size=None):
        # emulate current behavior: already sorted by size desc is not required for this test
        return list(fake_targets)

    monkeypatch.setattr(fs, "enumerate_targets", fake_enumerate_targets)

    # Run preview with exclude-zero & top 2
    res = runner.invoke(
        clean_app,
        [
            "preview",
            "--category",
            "temp",
            "--exclude-zero",
            "--min-size",
            "0",
            "--top",
            "2",
        ],
    )
    assert res.exit_code == 0, res.output
    # Should not contain the 0-byte entry
    assert "C:/Temp/a.tmp" not in res.output
    # Should show only 2 rows from the remaining 3 non-zero files
    assert res.output.count("C:/Temp/") == 2


def test_run_from_report_with_compat(monkeypatch, tmp_path):
    # Build a fake preview report that mixes schemas:
    # - items with "path"
    # - items with "from"
    # - legacy "files"
    report_data = {
        "run_id": "preview-TEST",
        "mode": "preview",
        "items": [{"path": "C:/Temp/alpha.tmp", "size": 10, "category": "temp"},
                  {"from": "C:/Temp/beta.tmp", "size": 20, "category": "temp"}],
        "files": ["C:/Temp/gamma.tmp", "C:/Temp/alpha.tmp"],  # alpha dup should be deduped
    }
    report_path = tmp_path / "preview.json"
    report_path.write_text(__import__("json").dumps(report_data), encoding="utf-8")

    # Spy: capture the args passed to execute_cleanup
    called = {}

    # execute_cleanup signature (current):
    # (categories, mode="quarantine", min_age_days=None, min_size=None,
    #  explicit_paths=None, dry_run=False, retries=0, retry_delay_ms=150)
    def fake_execute_cleanup(
        categories,
        mode="quarantine",
        min_age_days=None,
        min_size=None,
        explicit_paths=None,
        dry_run=False,
        retries=0,
        retry_delay_ms=150,
        **kwargs
    ):
        called["categories"] = categories
        called["mode"] = mode
        called["min_age_days"] = min_age_days
        called["min_size"] = min_size
        called["explicit_paths"] = explicit_paths
        called["dry_run"] = dry_run
        called["retries"] = retries
        called["retry_delay_ms"] = retry_delay_ms
        # Return a minimal valid report
        return {
            "run_id": "RUN-TEST",
            "stats": {"examined": len(explicit_paths or []), "moved": 0, "deleted": 0, "skipped": 0, "errors": 0, "bytes_reclaimed": 0},
            "items": [],
        }

    # load_report should return what we wrote; we can let real fs.load_report read from disk,
    # but to avoid file IO differences on Windows paths, just mock it:
    def fake_load_report(path: Path):
        return report_data

    monkeypatch.setattr(fs, "execute_cleanup", fake_execute_cleanup)
    monkeypatch.setattr(fs, "load_report", fake_load_report)

    # Invoke run with from-report + dry-run + retries
    res = runner.invoke(
        clean_app,
        [
            "run",
            "--from-report",
            str(report_path),
            "--dry-run",
            "--retries",
            "2",
            "--retry-delay-ms",
            "200",
        ],
    )
    assert res.exit_code == 0, res.output
    # Confirm flags plumbed correctly
    assert called["dry_run"] is True
    assert called["retries"] == 2
    assert called["retry_delay_ms"] == 200
    # When using --from-report, CLI should pass None for min_age/min_size (parity mode)
    assert called["min_age_days"] is None
    assert called["min_size"] is None
    # Categories should come from the CLI default if not specified explicitly
    assert isinstance(called["categories"], list) and len(called["categories"]) >= 1
    # explicit_paths must dedup and contain all three unique paths
    exp = called["explicit_paths"]
    assert exp is not None and set(exp) == {"C:/Temp/alpha.tmp", "C:/Temp/beta.tmp", "C:/Temp/gamma.tmp"}
