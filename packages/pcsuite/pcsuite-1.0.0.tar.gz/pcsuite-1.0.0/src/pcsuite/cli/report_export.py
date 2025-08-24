import typer
from rich.console import Console
from pathlib import Path
import json
from rich.table import Table

app = typer.Typer(help="Export reports to HTML/PDF")
console = Console()

@app.command()
def html(report: Path):
    """Export a JSON report to HTML."""
    with open(report, "r", encoding="utf-8") as f:
        data = json.load(f)
    html = ["<html><head><title>PCSuite Report</title></head><body>"]
    html.append(f"<h1>PCSuite Report: {report.name}</h1>")
    html.append(f"<pre>{json.dumps(data.get('stats', {}), indent=2)}</pre>")
    html.append("<table border=1><tr><th>File</th><th>Status</th><th>Size</th></tr>")
    for item in data.get("items", []):
        html.append(f"<tr><td>{item.get('from') or item.get('path')}</td><td>{item.get('status')}</td><td>{item.get('size', '')}</td></tr>")
    html.append("</table></body></html>")
    out = report.with_suffix(".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    console.print(f"[green]Exported:[/] {out}")

@app.command()
def pdf(report: Path):
    """Export a JSON report to PDF (requires pdfkit & wkhtmltopdf)."""
    try:
        import pdfkit
    except ImportError:
        console.print("[red]pdfkit not installed. Run 'pip install pdfkit'.")
        return
    html_file = report.with_suffix(".html")
    if not html_file.exists():
        html(report)
    out = report.with_suffix(".pdf")
    pdfkit.from_file(str(html_file), str(out))
    console.print(f"[green]Exported:[/] {out}")
