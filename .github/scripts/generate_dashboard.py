"""
.github/scripts/generate_dashboard.py
=======================================
Reads JSON test results and updates the GitHub Pages dashboard.
Python port of generate-dashboard.js from the reference repo.

Called by publish-report.yml with these env vars:
  BRANCH      — git branch name
  RUN_ID      — GitHub Actions run ID
  REPORT_PATH — path to downloaded reports artifact
  KEEP_RUNS   — how many runs to keep per branch (default 10)
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


KEEP_RUNS = int(os.environ.get("KEEP_RUNS", "10"))
BRANCH = os.environ.get("BRANCH", "main")
RUN_ID = os.environ.get("RUN_ID", "local")
BROWSER = os.environ.get("BROWSER", "chromium")
REPORT_PATH = Path(os.environ.get("REPORT_PATH", "downloaded-reports"))
HISTORY_FILE = Path("history.json")
RUNS_DIR = Path("runs")


def load_history() -> list:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def save_history(history: list):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def parse_results() -> dict:
    results_file = REPORT_PATH / "test-results.json"
    if not results_file.exists():
        return {"passed": 0, "failed": 1, "total": 1}

    data = json.loads(results_file.read_text())
    summary = data.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = passed + failed
    return {"passed": passed, "failed": failed, "total": total}


def copy_report():
    dest = RUNS_DIR / RUN_ID
    dest.mkdir(parents=True, exist_ok=True)
    src = REPORT_PATH / "index.html"
    if src.exists():
        shutil.copy(src, dest / "index.html")
    return str(dest / "index.html")


def cleanup_old_runs(history: list) -> list:
    branch_runs = [r for r in history if r.get("branch") == BRANCH]
    if len(branch_runs) > KEEP_RUNS:
        to_remove = branch_runs[:-KEEP_RUNS]
        for run in to_remove:
            old_dir = RUNS_DIR / run["run_id"]
            if old_dir.exists():
                shutil.rmtree(old_dir)
        history = [r for r in history if r not in to_remove]
    return history


def sparkline_svg(pass_rates: list[float]) -> str:
    """Generate a tiny SVG sparkline from a list of pass rates (0-100)."""
    if not pass_rates:
        return ""
    w, h = 80, 24
    n = len(pass_rates)
    step = w / max(n - 1, 1)
    points = [
        f"{round(i * step, 1)},{round(h - (r / 100) * h, 1)}"
        for i, r in enumerate(pass_rates)
    ]
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#4ade80" stroke-width="2"/>'
        f"</svg>"
    )


def generate_html(history: list) -> str:
    recent = history[-20:]
    pass_rates = [r["pass_rate"] for r in recent]
    spark = sparkline_svg(pass_rates)

    total_runs = len(history)
    total_passed = sum(r["passed"] for r in history)
    total_failed = sum(r["failed"] for r in history)
    overall_rate = round((total_passed / max(sum(r["total"] for r in history), 1)) * 100)

    rows = ""
    for r in reversed(history[-50:]):
        status = "✅" if r["failed"] == 0 else "❌"
        rate_bar = f'<div style="background:#4ade80;width:{r["pass_rate"]}%;height:8px;border-radius:4px"></div>'
        rows += f"""
        <tr>
          <td>{status}</td>
          <td>{r['timestamp']}</td>
          <td>{r['branch']}</td>
          <td>{r.get('browser','—')}</td>
          <td>{r['passed']}</td>
          <td>{r['failed']}</td>
          <td>{rate_bar} {r['pass_rate']}%</td>
          <td><a href="runs/{r['run_id']}/index.html" target="_blank">View</a></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Playwright Dashboard</title>
  <meta http-equiv="refresh" content="60">
  <style>
    body {{ font-family: system-ui, sans-serif; background:#0d1117; color:#c9d1d9; margin:0; padding:24px; }}
    h1 {{ color:#58a6ff; }}
    .cards {{ display:flex; gap:16px; margin:24px 0; flex-wrap:wrap; }}
    .card {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px 24px; min-width:140px; }}
    .card .label {{ font-size:12px; color:#8b949e; text-transform:uppercase; letter-spacing:.05em; }}
    .card .value {{ font-size:32px; font-weight:700; margin-top:4px; }}
    table {{ width:100%; border-collapse:collapse; background:#161b22; border-radius:8px; overflow:hidden; }}
    th {{ background:#21262d; padding:10px 14px; text-align:left; font-size:12px; color:#8b949e; text-transform:uppercase; }}
    td {{ padding:10px 14px; border-top:1px solid #21262d; font-size:13px; }}
    a {{ color:#58a6ff; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .spark {{ margin-top:8px; }}
  </style>
</head>
<body>
  <h1>🎭 Playwright Dashboard</h1>
  <p style="color:#8b949e">Auto-updated on every CI run · Last run: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

  <div class="cards">
    <div class="card"><div class="label">Total Runs</div><div class="value">{total_runs}</div></div>
    <div class="card"><div class="label">Tests Passed</div><div class="value" style="color:#4ade80">{total_passed}</div></div>
    <div class="card"><div class="label">Tests Failed</div><div class="value" style="color:#f85149">{total_failed}</div></div>
    <div class="card"><div class="label">Pass Rate</div><div class="value">{overall_rate}%</div></div>
  </div>

  <div class="spark"><strong>Pass rate trend (last 20 runs):</strong><br>{spark}</div>

  <h2 style="margin-top:32px">Run History</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th><th>Date</th><th>Branch</th><th>Browser</th>
        <th>Passed</th><th>Failed</th><th>Pass Rate</th><th>Report</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""


def main():
    results = parse_results()
    report_url = copy_report()

    passed = results["passed"]
    failed = results["failed"]
    total = results["total"]
    pass_rate = round((passed / max(total, 1)) * 100)

    history = load_history()
    history.append({
        "run_id": RUN_ID,
        "branch": BRANCH,
        "browser": BROWSER,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": pass_rate,
        "report": report_url,
    })
    history = cleanup_old_runs(history)
    save_history(history)

    Path("index.html").write_text(generate_html(history))
    print(f"Dashboard updated — run {RUN_ID}: {passed}/{total} passed ({pass_rate}%)")


if __name__ == "__main__":
    main()
