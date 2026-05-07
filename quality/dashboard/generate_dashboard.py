#!/usr/bin/env python3
"""Unified quality dashboard: CodeQL MISRA + Clang-Tidy + Coverage.

Usage (local):
    bazel run //quality/dashboard:generate_dashboard -- \\
        --csv            codeql_results/codeql-results.csv \\
        --clang-tidy-dir bazel-bin \\
        --lcov           <path>/_coverage/_coverage_report.dat \\
        --html           codeql_results/dashboard.html \\
        [--serve] [--port 8080]

Usage (CI):
    bazel run //quality/dashboard:generate_dashboard -- \\
        --csv            codeql_results/codeql-results.csv \\
        --clang-tidy-dir clang_tidy_results \\
        --lcov           coverage_results/coverage.dat \\
        --html           codeql_results/dashboard.html \\
        --github-summary
"""

import argparse
import csv
import html as _html
import http.server
import json
import os
import pathlib
import re
import sys
import threading
import webbrowser
from collections import Counter
from datetime import datetime, timezone


# ── severity helpers ──────────────────────────────────────────────────────────
_SEV_ORDER = {
    "critical": 0, "high": 1, "error": 1,
    "warning": 2, "medium": 2,
    "low": 3, "recommendation": 4, "note": 4,
}
_SEV_COLOUR = {
    "critical":       "#c0392b",
    "high":           "#e74c3c",
    "error":          "#e74c3c",
    "warning":        "#e67e22",
    "medium":         "#e67e22",
    "low":            "#f1c40f",
    "recommendation": "#3498db",
    "note":           "#95a5a6",
}


def _sev_key(s: str) -> int:
    return _SEV_ORDER.get(s.lower(), 99)


def _sev_colour(s: str) -> str:
    return _SEV_COLOUR.get(s.lower(), "#95a5a6")


def _badge(severity: str) -> str:
    c = _sev_colour(severity)
    return (f'<span class="badge" style="background:{c}">'
            f'{_html.escape(severity.upper())}</span>')


def _cov_colour(pct: float) -> str:
    if pct >= 90:
        return "#27ae60"
    if pct >= 70:
        return "#e67e22"
    return "#e74c3c"


def _cov_bar(pct: float) -> str:
    c = _cov_colour(pct)
    return (
        f'<div class="cov-bar-wrap">'
        f'<div class="cov-bar" style="width:{min(pct,100):.1f}%;background:{c}"></div>'
        f'</div>'
        f'<span style="color:{c};font-weight:600">{pct:.1f}%</span>'
    )


# ── CodeQL CSV ────────────────────────────────────────────────────────────────
# Columns: name, description, severity, message, path, start_line, start_col,
#          end_line, end_col
def load_codeql_csv(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) < 5:
                continue
            rows.append({
                "name":        row[0].strip(),
                "description": row[1].strip(),
                "severity":    row[2].strip(),
                "message":     row[3].strip(),
                "path":        row[4].strip(),
                "start_line":  row[5].strip() if len(row) > 5 else "",
            })
    return sorted(rows, key=lambda r: _sev_key(r["severity"]))


# ── Clang-Tidy reports ────────────────────────────────────────────────────────
# Full format:   /path/file.cc:line:col: warning: message [check-name]
# Simple format: warning: message [check-name]   (no location, e.g. builtins)
_CT_FULL_RE   = re.compile(r'^(.+?):(\d+):\d+: (warning|error): (.+?) \[([^\]]+)\]\s*$')
_CT_SIMPLE_RE = re.compile(r'^(warning|error): (.+?) \[([^\]]+)\]\s*$')


def load_clang_tidy(search_dir: pathlib.Path) -> list[dict]:
    if not search_dir.exists():
        return []
    findings: list[dict] = []
    seen: set[tuple] = set()
    for report_file in search_dir.rglob("*.AspectRulesLintClangTidy.report"):
        for line in report_file.read_text(encoding="utf-8", errors="replace").splitlines():
            m = _CT_FULL_RE.match(line)
            if m:
                fpath, lineno, severity, message, check = m.groups()
                key = (fpath, lineno, check, message[:80])
                if key not in seen:
                    seen.add(key)
                    findings.append({
                        "path": fpath, "line": lineno,
                        "severity": severity, "message": message, "check": check,
                    })
                continue
            m = _CT_SIMPLE_RE.match(line)
            if m:
                severity, message, check = m.groups()
                key = ("", "", check, message[:80])
                if key not in seen:
                    seen.add(key)
                    findings.append({
                        "path": "", "line": "",
                        "severity": severity, "message": message, "check": check,
                    })
    return sorted(findings, key=lambda r: (0 if r["severity"] == "error" else 1, r["path"]))


# ── Coverage (lcov) ───────────────────────────────────────────────────────────
def load_lcov(path: pathlib.Path) -> tuple[dict, list[dict]]:
    """Return (overall_summary_dict, per_file_list). Empty dicts/list if unavailable."""
    if not path or not path.is_file():
        return {}, []
    files: list[dict] = []
    cur: dict | None = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("SF:"):
            cur = {"file": line[3:], "lf": 0, "lh": 0,
                   "fnf": 0, "fnh": 0, "brf": 0, "brh": 0,
                   "_da_lf": 0, "_da_lh": 0}
        elif cur is None:
            continue
        elif line.startswith("DA:"):
            parts = line[3:].split(",")
            cur["_da_lf"] += 1
            if len(parts) >= 2:
                try:
                    if int(parts[1]) > 0:
                        cur["_da_lh"] += 1
                except ValueError:
                    pass
        elif line.startswith("LF:"):
            try: cur["lf"] = int(line[3:])
            except ValueError: pass
        elif line.startswith("LH:"):
            try: cur["lh"] = int(line[3:])
            except ValueError: pass
        elif line.startswith("FNF:"):
            try: cur["fnf"] = int(line[4:])
            except ValueError: pass
        elif line.startswith("FNH:"):
            try: cur["fnh"] = int(line[4:])
            except ValueError: pass
        elif line.startswith("BRF:"):
            try: cur["brf"] = int(line[4:])
            except ValueError: pass
        elif line.startswith("BRH:"):
            try: cur["brh"] = int(line[4:])
            except ValueError: pass
        elif line == "end_of_record" and cur is not None:
            # Prefer explicit LF/LH tags; fall back to counted DA lines
            if cur["lf"] == 0:
                cur["lf"] = cur["_da_lf"]
            if cur["lh"] == 0:
                cur["lh"] = cur["_da_lh"]
            files.append(cur)
            cur = None

    def pct(h: int, f: int) -> float:
        return round(100.0 * h / f, 1) if f else 0.0

    for f in files:
        f["line_pct"]   = pct(f["lh"],  f["lf"])
        f["func_pct"]   = pct(f["fnh"], f["fnf"])
        f["branch_pct"] = pct(f["brh"], f["brf"])

    total_lf  = sum(f["lf"]  for f in files)
    total_lh  = sum(f["lh"]  for f in files)
    total_fnf = sum(f["fnf"] for f in files)
    total_fnh = sum(f["fnh"] for f in files)
    total_brf = sum(f["brf"] for f in files)
    total_brh = sum(f["brh"] for f in files)

    summary = {
        "line_pct":   pct(total_lh,  total_lf),
        "func_pct":   pct(total_fnh, total_fnf),
        "branch_pct": pct(total_brh, total_brf),
        "lines":    f"{total_lh}/{total_lf}",
        "funcs":    f"{total_fnh}/{total_fnf}",
        "branches": f"{total_brh}/{total_brf}",
    }
    return summary, sorted(files, key=lambda f: f["line_pct"])


# ── History / KPI tracking ────────────────────────────────────────────────────
def load_history(path: pathlib.Path) -> list[dict]:
    """Load run history from a JSON file; return [] if absent or corrupt."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(path: pathlib.Path, history: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"History saved:    {path}  ({len(history)} runs)")


def _delta_badge(curr: float | int, prev: float | int,
                 higher_is_better: bool = False) -> str:
    """Coloured HTML badge: ↓N green=improvement, ↑N red=regression, = neutral."""
    diff = curr - prev
    if diff == 0:
        return '<span class="trend-eq">=</span>'
    improved = (diff < 0) if not higher_is_better else (diff > 0)
    cls = "trend-dn" if improved else "trend-up"
    sym = "↓" if diff < 0 else "↑"
    av = abs(diff)
    fmt = f"{av:.1f}" if isinstance(av, float) and av != int(av) else str(int(av))
    return f'<span class="{cls}">{sym}{fmt}</span>'


# ── HTML panels ───────────────────────────────────────────────────────────────
def _build_summary_cards(codeql_rows: list, clang_rows: list,
                         cov_summary: dict, prev_snap: dict | None = None) -> str:
    parts: list[str] = []
    p = prev_snap  # shorthand

    # CodeQL: per-severity cards; add a compact delta card when previous data exists
    cq_counts = Counter(r["severity"].lower() for r in codeql_rows)
    for sev in ["critical", "high", "error", "warning", "medium", "low",
                "recommendation", "note"]:
        n = cq_counts.get(sev, 0)
        if n:
            c = _sev_colour(sev)
            parts.append(
                f'<div class="card">'
                f'<div class="num" style="color:{c}">{n}</div>'
                f'<div class="label">CodeQL {sev}</div>'
                f'</div>'
            )
    if not codeql_rows:
        cq_d = (f'<div class="delta">{_delta_badge(0, p.get("codeql", 0), False)}</div>'
                if p else "")
        parts.append(
            f'<div class="card">'
            f'<div class="num" style="color:#27ae60">0</div>'
            f'{cq_d}'
            f'<div class="label">CodeQL findings</div>'
            f'</div>'
        )
    elif p is not None:
        d = _delta_badge(len(codeql_rows), p.get("codeql", len(codeql_rows)), False)
        parts.append(
            f'<div class="card" style="border-style:dashed;min-width:80px">'
            f'<div class="num" style="font-size:1.25rem">{d}</div>'
            f'<div class="label">CodeQL Δ</div>'
            f'</div>'
        )

    # Clang-Tidy card
    ct_errors = sum(1 for r in clang_rows if r["severity"] == "error")
    ct_colour = "#e74c3c" if ct_errors else ("#e67e22" if clang_rows else "#27ae60")
    ct_d = (
        f'<div class="delta">'
        f'{_delta_badge(len(clang_rows), p.get("clang_tidy", len(clang_rows)), False)}'
        f'</div>'
        if p else ""
    )
    parts.append(
        f'<div class="card">'
        f'<div class="num" style="color:{ct_colour}">{len(clang_rows)}</div>'
        f'{ct_d}'
        f'<div class="label">Clang-Tidy</div>'
        f'</div>'
    )

    # Coverage cards
    if cov_summary:
        for key, hist_key, label in [
            ("line_pct",   "line_cov",   "Line Cov"),
            ("func_pct",   "func_cov",   "Func Cov"),
            ("branch_pct", "branch_cov", "Branch Cov"),
        ]:
            v = cov_summary[key]
            c = _cov_colour(v)
            pv = p.get(hist_key) if p else None
            cov_d = (f'<div class="delta">{_delta_badge(v, pv, True)}</div>'
                     if pv is not None else "")
            parts.append(
                f'<div class="card">'
                f'<div class="num" style="color:{c}">{v:.1f}%</div>'
                f'{cov_d}'
                f'<div class="label">{label}</div>'
                f'</div>'
            )
    else:
        parts.append(
            '<div class="card">'
            '<div class="num" style="color:#95a5a6">N/A</div>'
            '<div class="label">Coverage</div>'
            '</div>'
        )
    return "\n".join(parts)


def _build_codeql_panel(rows: list[dict]) -> str:
    counts = Counter(r["severity"].lower() for r in rows)
    sev_opts = "\n".join(
        f'    <option value="{s}">{s.capitalize()} ({counts[s]})</option>'
        for s in ["critical", "high", "error", "warning", "medium", "low",
                  "recommendation", "note"]
        if s in counts
    )
    row_html = ""
    for r in rows:
        sev = r["severity"].lower()
        loc = _html.escape(r["path"])
        if r["start_line"]:
            loc += f':{r["start_line"]}'
        row_html += (
            f'  <tr data-sev="{_html.escape(sev)}">'
            f'<td>{_badge(r["severity"])}</td>'
            f'<td class="mono">{_html.escape(r["name"])}</td>'
            f'<td>{_html.escape(r["message"])}</td>'
            f'<td class="mono muted">{loc}</td>'
            f'</tr>\n'
        )
    empty = "" if rows else '<p class="empty-msg">No CodeQL findings — clean code!</p>'
    return (
        f'<div class="controls">\n'
        f'  <input id="cq-search" type="text" placeholder="Search message or path…"'
        f' oninput="cqFilter()" style="flex:1;min-width:200px"/>\n'
        f'  <select id="cq-sev" onchange="cqFilter()">\n'
        f'    <option value="">All severities</option>\n{sev_opts}\n  </select>\n'
        f'</div>\n'
        f'<table>\n'
        f'  <thead><tr>'
        f'<th onclick="cqSort(0)">Severity &#8597;</th>'
        f'<th onclick="cqSort(1)">Rule &#8597;</th>'
        f'<th onclick="cqSort(2)">Message &#8597;</th>'
        f'<th onclick="cqSort(3)">Location &#8597;</th>'
        f'</tr></thead>\n'
        f'  <tbody id="cq-tbody">\n{row_html}  </tbody>\n</table>\n{empty}'
    )


def _build_clang_panel(rows: list[dict]) -> str:
    counts = Counter(r["severity"] for r in rows)
    sev_opts = "\n".join(
        f'    <option value="{s}">{s.capitalize()} ({counts[s]})</option>'
        for s in ["error", "warning"] if s in counts
    )
    row_html = ""
    for r in rows:
        sev = r["severity"].lower()
        loc = _html.escape(r["path"])
        if r["line"]:
            loc += f':{r["line"]}'
        row_html += (
            f'  <tr data-sev="{_html.escape(sev)}">'
            f'<td>{_badge(r["severity"])}</td>'
            f'<td class="mono">{_html.escape(r["check"])}</td>'
            f'<td>{_html.escape(r["message"])}</td>'
            f'<td class="mono muted">{loc}</td>'
            f'</tr>\n'
        )
    empty = "" if rows else '<p class="empty-msg">No Clang-Tidy warnings — clean code!</p>'
    return (
        f'<div class="controls">\n'
        f'  <input id="ct-search" type="text" placeholder="Search message or check…"'
        f' oninput="ctFilter()" style="flex:1;min-width:200px"/>\n'
        f'  <select id="ct-sev" onchange="ctFilter()">\n'
        f'    <option value="">All severities</option>\n{sev_opts}\n  </select>\n'
        f'</div>\n'
        f'<table>\n'
        f'  <thead><tr>'
        f'<th onclick="ctSort(0)">Severity &#8597;</th>'
        f'<th onclick="ctSort(1)">Check &#8597;</th>'
        f'<th onclick="ctSort(2)">Message &#8597;</th>'
        f'<th onclick="ctSort(3)">Location &#8597;</th>'
        f'</tr></thead>\n'
        f'  <tbody id="ct-tbody">\n{row_html}  </tbody>\n</table>\n{empty}'
    )


def _build_coverage_panel(summary: dict, files: list[dict]) -> str:
    if not summary:
        return (
            '<p class="empty-msg">No coverage data available.<br>'
            'Run <code>bazel coverage //:calculator_test</code> and pass '
            '<code>--lcov &lt;path&gt;/_coverage/_coverage_report.dat</code></p>'
        )
    lc = _cov_colour(summary["line_pct"])
    fc = _cov_colour(summary["func_pct"])
    bc = _cov_colour(summary["branch_pct"])
    boxes = (
        f'<div class="cov-summary">'
        f'<div class="cov-box">'
        f'<div class="big" style="color:{lc}">{summary["line_pct"]:.1f}%</div>'
        f'<div class="sub">Line Coverage</div>'
        f'<div class="detail">{summary["lines"]} lines</div>'
        f'</div>'
        f'<div class="cov-box">'
        f'<div class="big" style="color:{fc}">{summary["func_pct"]:.1f}%</div>'
        f'<div class="sub">Function Coverage</div>'
        f'<div class="detail">{summary["funcs"]} functions</div>'
        f'</div>'
        f'<div class="cov-box">'
        f'<div class="big" style="color:{bc}">{summary["branch_pct"]:.1f}%</div>'
        f'<div class="sub">Branch Coverage</div>'
        f'<div class="detail">{summary["branches"]} branches</div>'
        f'</div>'
        f'</div>\n'
    )
    if not files:
        return boxes + '<p class="empty-msg">No per-file data.</p>'
    row_html = ""
    for f in files:
        fname = _html.escape(pathlib.Path(f["file"]).name or f["file"])
        lp, fp, bp = f["line_pct"], f["func_pct"], f["branch_pct"]
        row_html += (
            f'  <tr>'
            f'<td class="mono">{fname}</td>'
            f'<td data-val="{lp}">{_cov_bar(lp)}</td>'
            f'<td data-val="{fp}">{_cov_bar(fp)}</td>'
            f'<td data-val="{bp}">{_cov_bar(bp)}</td>'
            f'<td class="mono muted">{f["lh"]}/{f["lf"]}</td>'
            f'</tr>\n'
        )
    table = (
        f'<table>\n'
        f'  <thead><tr>'
        f'<th>File</th>'
        f'<th onclick="cvSort(1)" style="cursor:pointer">Lines &#8597;</th>'
        f'<th onclick="cvSort(2)" style="cursor:pointer">Functions &#8597;</th>'
        f'<th onclick="cvSort(3)" style="cursor:pointer">Branches &#8597;</th>'
        f'<th>Lines (hit/total)</th>'
        f'</tr></thead>\n'
        f'  <tbody id="cv-tbody">\n{row_html}  </tbody>\n</table>'
    )
    return boxes + table


# ── KPI / Trends panel ────────────────────────────────────────────────────────
def _build_kpi_panel(history: list[dict]) -> str:
    if not history:
        return (
            '<p class="empty-msg">No history yet.<br>'
            'Pass <code>--history quality_history.json</code> to start tracking.</p>'
        )
    if len(history) < 2:
        return (
            f'<p class="empty-msg">Only 1 run recorded so far '
            f'({_html.escape(history[0].get("date", ""))}).<br>'
            f'Trends will appear after the next run.</p>'
        )

    latest = history[-1]
    first  = history[0]
    prev   = history[-2]

    # ── KPI fix-rate cards ──
    def _fix_card(label: str, key: str, hib: bool, unit: str = "") -> str:
        curr = latest.get(key)
        prv  = prev.get(key)
        orig = first.get(key)
        if curr is None:
            return (f'<div class="card"><div class="num">N/A</div>'
                    f'<div class="label">{label}</div></div>')
        disp = f"{curr:.1f}{unit}" if isinstance(curr, float) else f"{curr}{unit}"
        d_html = _delta_badge(curr, prv, hib) if prv is not None else ""
        if orig is not None and orig != 0:
            rate = (orig - curr) / orig * 100 if not hib else (curr - orig) / orig * 100
            rc = "#27ae60" if rate >= 0 else "#e74c3c"
            fix_html = f'<span style="color:{rc};font-size:0.78rem">{rate:+.1f}% vs start</span>'
        else:
            fix_html = ""
        return (
            f'<div class="card">'
            f'<div class="num">{disp}</div>'
            f'<div class="delta">{d_html} vs prev</div>'
            f'<div class="label">{label}<br>{fix_html}</div>'
            f'</div>'
        )

    kpi_html = (
        '<h3 class="section-title">Error Fix KPIs</h3>'
        '<div class="cards" style="margin-bottom:2rem;">'
        + _fix_card("CodeQL Findings",     "codeql",     False)
        + _fix_card("Clang-Tidy Warnings", "clang_tidy", False)
        + _fix_card("Line Coverage",       "line_cov",   True,  "%")
        + _fix_card("Branch Coverage",     "branch_cov", True,  "%")
        + '</div>'
    )

    # ── Sparklines ──
    def _spark(h: int, bg: str, title: str) -> str:
        return (f'<div class="spark-bar" style="height:{max(2, h)}px;background:{bg}"'
                f' title="{_html.escape(title)}"></div>')

    max_cq = max((s.get("codeql") or 0 for s in history), default=1) or 1
    cq_bars = "".join(
        _spark(int((s.get("codeql") or 0) / max_cq * 30),
               "#e74c3c" if (s.get("codeql") or 0) > 0 else "#27ae60",
               f'{s.get("date","?")} — {s.get("codeql", 0)} findings')
        for s in history
    )
    cov_bars = "".join(
        _spark(int((s.get("line_cov") or 0) / 100 * 30),
               _cov_colour(s.get("line_cov") or 0),
               f'{s.get("date","?")} — {(s.get("line_cov") or 0):.1f}%')
        for s in history
    )
    first_cq, last_cq = first.get("codeql") or 0, latest.get("codeql") or 0
    cq_trend = ("↓ Improving" if last_cq < first_cq
                else "↑ Worsening" if last_cq > first_cq else "→ Stable")

    kpi_html += (
        '<h3 class="section-title">Trend Sparklines</h3>'
        '<div style="display:flex;gap:2rem;flex-wrap:wrap;margin-bottom:2rem;">'
        f'<div><div class="muted" style="font-size:0.8rem;margin-bottom:4px">'
        f'CodeQL findings — {cq_trend}</div>'
        f'<div class="spark-wrap">{cq_bars}</div></div>'
        f'<div><div class="muted" style="font-size:0.8rem;margin-bottom:4px">'
        f'Line coverage %</div>'
        f'<div class="spark-wrap">{cov_bars}</div></div>'
        '</div>'
    )

    # ── History table ──
    def _fi(curr, ps, key, hib=False):
        if curr is None: return "N/A"
        pv = ps.get(key) if ps else None
        d = f' {_delta_badge(curr, pv, hib)}' if pv is not None else ''
        return f'{curr}{d}'

    def _fc(curr, ps, key):
        if curr is None: return "N/A"
        c = _cov_colour(curr)
        pv = ps.get(key) if ps else None
        d = f' {_delta_badge(curr, pv, True)}' if pv is not None else ''
        return f'<span style="color:{c}">{curr:.1f}%</span>{d}'

    kpi_html += (
        '<h3 class="section-title">Run History</h3>'
        '<table>\n'
        '  <thead><tr>'
        '<th>Date</th><th>CodeQL</th><th>Clang-Tidy</th>'
        '<th>Line Cov</th><th>Func Cov</th><th>Branch Cov</th>'
        '</tr></thead>\n'
        '  <tbody>\n'
    )
    for i, snap in enumerate(reversed(history)):
        orig_idx = len(history) - 1 - i
        is_latest = (i == 0)
        row_sty = ' style="background:var(--surface)"' if is_latest else ''
        ps = history[orig_idx - 1] if orig_idx > 0 else None
        now_label = ('&nbsp;<span style="font-size:0.72rem;color:var(--accent)">now</span>'
                     if is_latest else "")
        kpi_html += (
            f'  <tr{row_sty}>'
            f'<td class="mono">{_html.escape(snap.get("date",""))}{now_label}</td>'
            f'<td>{_fi(snap.get("codeql"),     ps, "codeql")}</td>'
            f'<td>{_fi(snap.get("clang_tidy"), ps, "clang_tidy")}</td>'
            f'<td>{_fc(snap.get("line_cov"),   ps, "line_cov")}</td>'
            f'<td>{_fc(snap.get("func_cov"),   ps, "func_cov")}</td>'
            f'<td>{_fc(snap.get("branch_cov"), ps, "branch_cov")}</td>'
            f'</tr>\n'
        )
    kpi_html += '  </tbody>\n</table>'
    return kpi_html


# ── HTML template ─────────────────────────────────────────────────────────────
_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Quality Dashboard</title>
<style>
  :root {{
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          padding: 2rem; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 0.25rem; }}
  .meta {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 1.5rem; }}
  /* cards */
  .cards {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
  .card {{ background: var(--surface); border: 1px solid var(--border);
           border-radius: 8px; padding: 0.9rem 1.25rem; min-width: 110px; text-align: center; }}
  .card .num {{ font-size: 1.8rem; font-weight: 700; }}
  .card .label {{ color: var(--muted); font-size: 0.75rem; text-transform: uppercase; margin-top: 4px; }}
  /* tabs */
  .tabs {{ display: flex; border-bottom: 2px solid var(--border); margin-bottom: 1.5rem; }}
  .tab-btn {{ background: none; border: none; border-bottom: 3px solid transparent;
              margin-bottom: -2px; padding: 0.6rem 1.25rem; color: var(--muted);
              cursor: pointer; font-size: 0.95rem; font-weight: 500; }}
  .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
  .tab-btn:hover {{ color: var(--text); }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}
  /* controls */
  .controls {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.75rem; }}
  .controls input, .controls select {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
    color: var(--text); padding: 0.4rem 0.8rem; font-size: 0.9rem;
  }}
  /* table */
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  thead th {{ background: var(--surface); border-bottom: 2px solid var(--border);
              padding: 0.6rem 0.8rem; text-align: left; color: var(--muted);
              text-transform: uppercase; font-size: 0.75rem;
              cursor: pointer; user-select: none; white-space: nowrap; }}
  thead th:hover {{ color: var(--accent); }}
  tbody tr {{ border-bottom: 1px solid var(--border); }}
  tbody tr:hover {{ background: var(--surface); }}
  td {{ padding: 0.5rem 0.8rem; vertical-align: top; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px;
            font-size: 0.75rem; font-weight: 600; color: #fff; white-space: nowrap; }}
  .mono {{ font-family: monospace; font-size: 0.82rem; }}
  .muted {{ color: var(--muted); }}
  .empty-msg {{ text-align: center; padding: 3rem; color: var(--muted); }}
  /* coverage */
  .cov-bar-wrap {{ display: inline-block; background: var(--border); border-radius: 4px;
                   height: 6px; width: 80px; vertical-align: middle; margin-right: 6px; }}
  .cov-bar {{ height: 6px; border-radius: 4px; }}
  .cov-summary {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem; }}
  .cov-box {{ background: var(--surface); border: 1px solid var(--border);
              border-radius: 8px; padding: 1rem 1.5rem; text-align: center; min-width: 140px; }}
  .cov-box .big {{ font-size: 2rem; font-weight: 700; }}
  .cov-box .sub {{ color: var(--muted); font-size: 0.8rem; margin-top: 2px; }}
  .cov-box .detail {{ color: var(--muted); font-size: 0.75rem; margin-top: 2px; }}
  /* trend badges */
  .trend-up {{ color: #e74c3c; font-weight: 700; font-size: 0.75rem; margin-left: 2px; }}
  .trend-dn {{ color: #27ae60; font-weight: 700; font-size: 0.75rem; margin-left: 2px; }}
  .trend-eq {{ color: #8b949e; font-weight: 700; font-size: 0.75rem; margin-left: 2px; }}
  .card .delta {{ font-size: 0.8rem; min-height: 1.1em; margin-top: 2px; }}
  .section-title {{ color: var(--muted); font-size: 0.85rem; text-transform: uppercase;
                    letter-spacing: 0.05em; margin-bottom: 0.75rem; font-weight: 600;
                    margin-top: 1.25rem; }}
  /* sparkline */
  .spark-wrap {{ display: flex; align-items: flex-end; gap: 3px; height: 32px;
                 background: var(--surface); padding: 4px 6px; border-radius: 4px; }}
  .spark-bar {{ width: 10px; border-radius: 2px 2px 0 0; min-height: 2px;
                cursor: default; transition: opacity 0.15s; }}
  .spark-bar:hover {{ opacity: 0.7; }}
</style>
</head>
<body>
<h1>Quality Dashboard</h1>
<p class="meta">Generated: {timestamp}</p>

<div class="cards">
{summary_cards}
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="showTab('codeql',this)">CodeQL ({codeql_count})</button>
  <button class="tab-btn" onclick="showTab('clang',this)">Clang-Tidy ({clang_count})</button>
  <button class="tab-btn" onclick="showTab('coverage',this)">Coverage ({coverage_label})</button>
  <button class="tab-btn" onclick="showTab('kpi',this)">KPI / Trends ({kpi_runs} runs)</button>
</div>

<div id="tab-codeql" class="panel active">
{codeql_panel}
</div>

<div id="tab-clang" class="panel">
{clang_panel}
</div>

<div id="tab-coverage" class="panel">
{coverage_panel}
</div>

<div id="tab-kpi" class="panel">
{kpi_panel}
</div>

<script>
function showTab(name, btn) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}}
// CodeQL filter + sort
const cqRows = Array.from(document.querySelectorAll('#cq-tbody tr'));
function cqFilter() {{
  const q = document.getElementById('cq-search').value.toLowerCase();
  const s = document.getElementById('cq-sev').value.toLowerCase();
  cqRows.forEach(r => {{
    r.style.display = ((!q || r.textContent.toLowerCase().includes(q))
                    && (!s || (r.dataset.sev||'') === s)) ? '' : 'none';
  }});
}}
let cqDir=1; function cqSort(c) {{ const tb=document.getElementById('cq-tbody');
  [...tb.querySelectorAll('tr')].sort((a,b)=>(a.cells[c]?.textContent||'').localeCompare(b.cells[c]?.textContent||'')*cqDir)
  .forEach(r=>tb.appendChild(r)); cqDir*=-1; }}
// Clang-Tidy filter + sort
const ctRows = Array.from(document.querySelectorAll('#ct-tbody tr'));
function ctFilter() {{
  const q = document.getElementById('ct-search').value.toLowerCase();
  const s = document.getElementById('ct-sev').value.toLowerCase();
  ctRows.forEach(r => {{
    r.style.display = ((!q || r.textContent.toLowerCase().includes(q))
                    && (!s || (r.dataset.sev||'') === s)) ? '' : 'none';
  }});
}}
let ctDir=1; function ctSort(c) {{ const tb=document.getElementById('ct-tbody');
  [...tb.querySelectorAll('tr')].sort((a,b)=>(a.cells[c]?.textContent||'').localeCompare(b.cells[c]?.textContent||'')*ctDir)
  .forEach(r=>tb.appendChild(r)); ctDir*=-1; }}
// Coverage sort (numeric)
let cvDir=1; function cvSort(c) {{ const tb=document.getElementById('cv-tbody');
  [...tb.querySelectorAll('tr')].sort((a,b)=>
    (parseFloat(a.cells[c]?.dataset.val||0)-parseFloat(b.cells[c]?.dataset.val||0))*cvDir)
  .forEach(r=>tb.appendChild(r)); cvDir*=-1; }}
</script>
</body>
</html>
"""


def build_html(codeql_rows: list[dict], clang_rows: list[dict],
               cov_summary: dict, cov_files: list[dict],
               history: list[dict], timestamp: str) -> str:
    prev_snap = history[-2] if len(history) >= 2 else None
    return _HTML_TEMPLATE.format(
        timestamp=_html.escape(timestamp),
        summary_cards=_build_summary_cards(codeql_rows, clang_rows, cov_summary, prev_snap),
        codeql_count=len(codeql_rows),
        clang_count=len(clang_rows),
        coverage_label=f'{cov_summary["line_pct"]:.1f}%' if cov_summary else "N/A",
        kpi_runs=len(history),
        codeql_panel=_build_codeql_panel(codeql_rows),
        clang_panel=_build_clang_panel(clang_rows),
        coverage_panel=_build_coverage_panel(cov_summary, cov_files),
        kpi_panel=_build_kpi_panel(history),
    )


# ── GitHub Actions step summary ───────────────────────────────────────────────
def write_github_summary(codeql_rows: list[dict], clang_rows: list[dict],
                         cov_summary: dict, history: list[dict],
                         summary_path: str) -> None:
    lines = ["## Quality Dashboard\n"]

    # CodeQL
    lines.append("### CodeQL (MISRA C++)\n")
    if not codeql_rows:
        lines.append("**No findings.** :white_check_mark:\n")
    else:
        counts = Counter(r["severity"].lower() for r in codeql_rows)
        lines += [f"**Total: {len(codeql_rows)} findings**\n",
                  "| Severity | Count |", "|----------|------:|"]
        for sev in ["critical","high","error","warning","medium","low","recommendation","note"]:
            if sev in counts:
                lines.append(f"| {sev.capitalize()} | {counts[sev]} |")
        lines.append("")

    # Clang-Tidy
    lines.append("### Clang-Tidy\n")
    if not clang_rows:
        lines.append("**No warnings.** :white_check_mark:\n")
    else:
        counts = Counter(r["severity"] for r in clang_rows)
        lines += [f"**Total: {len(clang_rows)} warnings**\n",
                  "| Severity | Count |", "|----------|------:|"]
        for sev in ["error", "warning"]:
            if sev in counts:
                lines.append(f"| {sev.capitalize()} | {counts[sev]} |")
        lines.append("")

    # Coverage
    lines.append("### Coverage\n")
    if cov_summary:
        lines += ["| Metric | Value |", "|--------|-------|",
                  f"| Lines | {cov_summary['line_pct']:.1f}% ({cov_summary['lines']}) |",
                  f"| Functions | {cov_summary['func_pct']:.1f}% ({cov_summary['funcs']}) |",
                  f"| Branches | {cov_summary['branch_pct']:.1f}% ({cov_summary['branches']}) |"]
    else:
        lines.append("Coverage data not available.\n")

    # KPI trends (when ≥2 runs exist)
    if len(history) >= 2:
        prev = history[-2]
        curr = history[-1]
        lines += ["", "### KPI Trend vs Previous Run\n",
                  "| Metric | Prev | Now | Δ |",
                  "|--------|------|-----|---|"]
        for label, key, hib in [
            ("CodeQL findings",    "codeql",     False),
            ("Clang-Tidy warnings","clang_tidy", False),
            ("Line coverage %",    "line_cov",   True),
            ("Branch coverage %",  "branch_cov", True),
        ]:
            pv = prev.get(key)
            cv = curr.get(key)
            if pv is not None and cv is not None:
                diff = cv - pv
                sym = "↓" if diff < 0 else ("↑" if diff > 0 else "=")
                good = (diff < 0) if not hib else (diff > 0)
                icon = "✅" if good else ("⚠️" if diff != 0 else "")
                fmt = f"{abs(diff):.1f}" if isinstance(diff, float) else str(abs(int(diff)))
                lines.append(f"| {label} | {pv} | {cv} | {sym}{fmt} {icon} |")
        if len(history) >= 2:
            first = history[0]
            lines.append("")
            lines.append(f"_Tracking since {first.get('date','start')} "
                         f"({len(history)} runs recorded)_")

    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description="Generate unified quality dashboard")
    parser.add_argument("--csv",            default="codeql_results/codeql-results.csv",
                        help="CodeQL CSV results file")
    parser.add_argument("--clang-tidy-dir", default="bazel-bin",
                        help="Directory containing *.AspectRulesLintClangTidy.report files")
    parser.add_argument("--lcov",           default="",
                        help="Path to lcov coverage .dat file")
    parser.add_argument("--html",           default="codeql_results/dashboard.html",
                        help="Output HTML file")
    parser.add_argument("--github-summary", action="store_true",
                        help="Append markdown to $GITHUB_STEP_SUMMARY")
    parser.add_argument("--history",        default="codeql_results/quality_history.json",
                        help="JSON file that accumulates per-run snapshots for KPI tracking")
    parser.add_argument("--serve",          action="store_true",
                        help="Serve dashboard locally and open in browser")
    parser.add_argument("--port",           type=int, default=8080,
                        help="HTTP server port (default: 8080)")
    args = parser.parse_args()

    # Resolve relative paths vs. BUILD_WORKSPACE_DIRECTORY (set by bazel run)
    _ws = pathlib.Path(os.environ.get("BUILD_WORKSPACE_DIRECTORY", pathlib.Path.cwd()))

    def _resolve(p: str) -> pathlib.Path:
        pp = pathlib.Path(p)
        return pp if pp.is_absolute() else _ws / pp

    csv_path       = _resolve(args.csv)
    clang_tidy_dir = _resolve(args.clang_tidy_dir)
    lcov_path      = _resolve(args.lcov) if args.lcov else pathlib.Path("")
    html_path      = _resolve(args.html)
    hist_path      = _resolve(args.history)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    codeql_rows             = load_codeql_csv(csv_path)
    clang_rows              = load_clang_tidy(clang_tidy_dir)
    cov_summary, cov_files  = load_lcov(lcov_path)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Append current run to history, then save
    history = load_history(hist_path)
    current_snap = {
        "date":       timestamp,
        "codeql":     len(codeql_rows),
        "clang_tidy": len(clang_rows),
        "line_cov":   cov_summary.get("line_pct")   if cov_summary else None,
        "func_cov":   cov_summary.get("func_pct")   if cov_summary else None,
        "branch_cov": cov_summary.get("branch_pct") if cov_summary else None,
    }
    history.append(current_snap)
    save_history(hist_path, history)

    html_content = build_html(codeql_rows, clang_rows, cov_summary, cov_files, history, timestamp)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"Dashboard written to: {html_path}")
    print(f"  CodeQL:     {len(codeql_rows)} findings")
    print(f"  Clang-Tidy: {len(clang_rows)} warnings")
    if cov_summary:
        print(f"  Coverage:   {cov_summary['line_pct']:.1f}% lines  "
              f"{cov_summary['func_pct']:.1f}% funcs  "
              f"{cov_summary['branch_pct']:.1f}% branches")
    else:
        print("  Coverage:   N/A")

    if args.github_summary:
        summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_file:
            write_github_summary(codeql_rows, clang_rows, cov_summary, history, summary_file)
        else:
            print("Warning: --github-summary set but $GITHUB_STEP_SUMMARY not defined",
                  file=sys.stderr)

    if args.serve:
        serve_dir = html_path.parent.resolve()
        url = f"http://localhost:{args.port}/{html_path.name}"

        class _QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, fmt, *a):
                pass

        try:
            server = http.server.HTTPServer(
                ("localhost", args.port),
                lambda *a, **kw: _QuietHandler(*a, directory=str(serve_dir), **kw),
            )
        except OSError as e:
            print(f"Cannot start server on port {args.port}: {e}", file=sys.stderr)
            print(f"Open manually: {html_path}")
            return 0
        print(f"Serving dashboard at {url}  (Ctrl-C to stop)")
        threading.Timer(0.3, webbrowser.open, args=[url]).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

