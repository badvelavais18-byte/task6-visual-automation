"""
Task 6 — Visual Automation
report_generator.py  ·  Self-contained HTML report with inline base64 images.

The report acts as a merge gate:
  ✅ MERGE APPROVED  — all visual checks passed
  ❌ MERGE BLOCKED   — at least one visual check failed
"""

import base64
import os
import time
from datetime import datetime
from typing import Any, Dict, List

from config import DIRS, SLEEP, DIFF_THRESHOLD_PCT


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def generate_report(results: List[Dict[str, Any]], name: str = "visual_report") -> str:
    """
    Generate a self-contained HTML visual regression report.

    Args:
        results:  List of result dicts returned by visual_comparator.compare().
        name:     Output filename stem (without .html).

    Returns:
        Absolute path to the saved HTML report.
    """
    time.sleep(SLEEP["after_compare"])    # ✅ SLEEP: before building report

    ts      = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    passed  = sum(1 for r in results if r.get("passed") is True)
    failed  = sum(1 for r in results if r.get("passed") is False)
    total   = len(results)
    gate_ok = failed == 0

    gate_label = "✅  MERGE APPROVED — all visual checks passed" if gate_ok \
                 else f"❌  MERGE BLOCKED — {failed} visual check(s) failed"
    gate_color = "#1a7f37" if gate_ok else "#cf222e"
    gate_bg    = "#dcfce7" if gate_ok else "#ffeef0"

    rows_html = "".join(_build_row(r) for r in results)

    html = _HTML_TEMPLATE.format(
        timestamp     = ts,
        threshold     = DIFF_THRESHOLD_PCT,
        gate_label    = gate_label,
        gate_color    = gate_color,
        gate_bg       = gate_bg,
        total         = total,
        passed        = passed,
        failed        = failed,
        rows          = rows_html,
    )

    report_path = os.path.join(DIRS["reports"], f"{name}.html")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    time.sleep(SLEEP["after_capture"])    # ✅ SLEEP: after file I/O

    print(f"\n📄  Report saved → {report_path}")
    return report_path


# ──────────────────────────────────────────────────────────────────────────────
# Row Builders
# ──────────────────────────────────────────────────────────────────────────────

def _build_row(r: Dict[str, Any]) -> str:
    if r.get("error"):
        return _error_row(r)

    status     = "PASS" if r["passed"] else "FAIL"
    row_bg     = "#f0fdf4" if r["passed"] else "#fff5f5"
    badge_bg   = "#1a7f37" if r["passed"] else "#cf222e"
    diff_bar   = _diff_bar(r["diff_pct"], r["threshold_pct"])

    return f"""
        <tr style="background:{row_bg}">
          <td><b>{r.get('page', '—')}</b></td>
          <td>{r.get('viewport', '—')}</td>
          <td>
            <span style="background:{badge_bg};color:#fff;padding:2px 9px;
                         border-radius:12px;font-size:.82em;font-weight:600">
              {status}
            </span>
          </td>
          <td>{diff_bar}</td>
          <td>{_img_tag(r.get('baseline_path', ''))}</td>
          <td>{_img_tag(r.get('actual_path', ''))}</td>
          <td>{_img_tag(r.get('diff_path', ''))}</td>
        </tr>"""


def _error_row(r: Dict[str, Any]) -> str:
    return f"""
        <tr style="background:#fffbeb">
          <td>{r.get('page', '—')}</td>
          <td>{r.get('viewport', '—')}</td>
          <td>
            <span style="background:#9a6700;color:#fff;padding:2px 9px;
                         border-radius:12px;font-size:.82em;font-weight:600">
              SKIP
            </span>
          </td>
          <td colspan="4" style="color:#9a6700;font-size:.88em">{r.get('error','—')}</td>
        </tr>"""


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _img_tag(path: str, width: int = 175) -> str:
    """Embed image as inline base64 for a portable, self-contained report."""
    if not path or not os.path.exists(path):
        return "<span style='color:#999;font-size:.8em'>—</span>"
    try:
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        return (
            f'<img src="data:image/png;base64,{b64}" width="{width}" '
            f'style="border:1px solid #d0d7de;border-radius:4px;display:block">'
        )
    except Exception:
        return "<span style='color:#999;font-size:.8em'>load error</span>"


def _diff_bar(diff_pct: float, threshold_pct: float) -> str:
    """Render a compact progress-bar showing diff vs threshold."""
    fill  = min(diff_pct / max(threshold_pct * 2, 0.01) * 100, 100)
    color = "#cf222e" if diff_pct > threshold_pct else "#1a7f37"
    return (
        f'<div style="font-size:.82em;margin-bottom:4px">'
        f'{diff_pct}% &nbsp;<span style="color:#636c76">/ {threshold_pct}% threshold</span></div>'
        f'<div style="background:#e5e7eb;border-radius:4px;height:7px;width:130px">'
        f'<div style="height:7px;border-radius:4px;width:{fill}%;background:{color}"></div></div>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# HTML Template
# ──────────────────────────────────────────────────────────────────────────────

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Visual Regression Report</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body   {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: #f6f8fa; color: #1f2328; padding: 28px 32px; }}
    h1     {{ font-size: 1.45rem; font-weight: 700; margin-bottom: 4px; }}
    .meta  {{ color: #636c76; font-size: .85rem; margin-bottom: 20px; }}
    .gate  {{ display: inline-block; padding: 10px 18px; border-radius: 8px;
              font-weight: 700; font-size: .95rem;
              background: {{gate_bg}}; color: {{gate_color}};
              border: 1.5px solid {{gate_color}}; margin-bottom: 22px; }}
    .stats {{ display: flex; gap: 16px; margin-bottom: 26px; flex-wrap: wrap; }}
    .stat  {{ background: #fff; border: 1px solid #d0d7de; border-radius: 8px;
              padding: 12px 22px; text-align: center; min-width: 90px; }}
    .num   {{ font-size: 1.9rem; font-weight: 700; line-height: 1.1; }}
    .lbl   {{ font-size: .78rem; color: #636c76; margin-top: 2px; }}
    table  {{ width: 100%; border-collapse: collapse; background: #fff;
              border: 1px solid #d0d7de; border-radius: 10px; overflow: hidden; }}
    th     {{ background: #f6f8fa; padding: 9px 12px; border-bottom: 1px solid #d0d7de;
              text-align: left; font-size: .78rem; text-transform: uppercase;
              letter-spacing: .04em; color: #636c76; }}
    td     {{ padding: 10px 12px; border-bottom: 1px solid #f0f0f0;
              vertical-align: middle; font-size: .88rem; }}
    tr:last-child td {{ border-bottom: none; }}
  </style>
</head>
<body>
  <h1>📸 Visual Regression Report</h1>
  <p class="meta">Generated: {timestamp} &nbsp;·&nbsp; Pixel diff threshold: {threshold}%</p>

  <div class="gate" style="background:{gate_bg};color:{gate_color};border-color:{gate_color}">
    {gate_label}
  </div>

  <div class="stats">
    <div class="stat">
      <div class="num">{total}</div>
      <div class="lbl">Total</div>
    </div>
    <div class="stat">
      <div class="num" style="color:#1a7f37">{passed}</div>
      <div class="lbl">Passed</div>
    </div>
    <div class="stat">
      <div class="num" style="color:#cf222e">{failed}</div>
      <div class="lbl">Failed</div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Page</th>
        <th>Viewport</th>
        <th>Status</th>
        <th>Pixel Diff</th>
        <th>Baseline</th>
        <th>Actual</th>
        <th>Diff Overlay</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>"""
