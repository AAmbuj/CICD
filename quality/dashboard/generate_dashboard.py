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

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

_TEMPLATE_DIR = pathlib.Path(__file__).parent

# ── Helpers exposed to the Jinja2 template ────────────────────────────────────
_SEV_COLOUR = {
    "critical": "#c0392b", "high": "#e74c3c", "error": "#e74c3c",
    "warning": "#e67e22",  "medium": "#e67e22", "low": "#f1c40f",
    "recommendation": "#3498db", "note": "#95a5a6",
}
_SEV_ORDER = {"critical":0,"high":1,"error":1,"warning":2,"medium":2,"low":3,"recommendation":4,"note":4}


def _sev_colour(s: str) -> str:
    return _SEV_COLOUR.get(str(s).lower(), "#95a5a6")


def _cov_colour(pct) -> str:
    pct = float(pct or 0)
    return "#27ae60" if pct >= 90 else ("#e67e22" if pct >= 70 else "#e74c3c")


def _delta_badge(curr, prev, higher_is_better: bool) -> Markup:
    try:
        diff = float(curr) - float(prev)
    except (TypeError, ValueError):
        return Markup("")
    if diff == 0:
        return Markup('<span class="trend-eq">=</span>')
    improved = (diff < 0) if not higher_is_better else (diff > 0)
    cls = "trend-dn" if improved else "trend-up"
    sym = "↓" if diff < 0 else "↑"
    fmt = f"{abs(diff):.1f}" if abs(diff) != int(abs(diff)) else str(int(abs(diff)))
    return Markup(f'<span class="{cls}">{sym}{fmt}</span>')


# ── Data parsers ──────────────────────────────────────────────────────────────
def load_codeql_csv(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) < 5:
                continue
            rows.append({"name": row[0].strip(), "description": row[1].strip(),
                         "severity": row[2].strip(), "message": row[3].strip(),
                         "path": row[4].strip(),
                         "start_line": row[5].strip() if len(row) > 5 else ""})
    return sorted(rows, key=lambda r: _SEV_ORDER.get(r["severity"].lower(), 99))


_CT_FULL_RE   = re.compile(r'^(.+?):(\d+):\d+: (warning|error): (.+?) \[([^\]]+)\]\s*$')
_CT_SIMPLE_RE = re.compile(r'^(warning|error): (.+?) \[([^\]]+)\]\s*$')


def load_clang_tidy(search_dir: pathlib.Path) -> list[dict]:
    if not search_dir.exists():
        return []
    findings, seen = [], set()
    for report_file in search_dir.rglob("*.AspectRulesLintClangTidy.report"):
        for line in report_file.read_text(encoding="utf-8", errors="replace").splitlines():
            m = _CT_FULL_RE.match(line)
            if m:
                fpath, lineno, sev, msg, check = m.groups()
                key = (fpath, lineno, check, msg[:80])
                if key not in seen:
                    seen.add(key)
                    findings.append({"path": fpath, "line": lineno,
                                     "severity": sev, "message": msg, "check": check})
                continue
            m = _CT_SIMPLE_RE.match(line)
            if m:
                sev, msg, check = m.groups()
                key = ("", "", check, msg[:80])
                if key not in seen:
                    seen.add(key)
                    findings.append({"path": "", "line": "",
                                     "severity": sev, "message": msg, "check": check})
    return sorted(findings, key=lambda r: (0 if r["severity"] == "error" else 1, r["path"]))


def load_lcov(path: pathlib.Path) -> tuple[dict, list[dict]]:
    if not path or not path.is_file():
        return {}, []
    files, cur = [], None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("SF:"):
            cur = {"file": line[3:], "lf":0,"lh":0,"fnf":0,"fnh":0,"brf":0,"brh":0,"_lf":0,"_lh":0}
        elif cur is None:
            continue
        elif line.startswith("DA:"):
            parts = line[3:].split(",")
            cur["_lf"] += 1
            if len(parts) >= 2:
                try:
                    if int(parts[1]) > 0: cur["_lh"] += 1
                except ValueError: pass
        elif line.startswith("LF:"): cur["lf"] = int(line[3:] or 0)
        elif line.startswith("LH:"): cur["lh"] = int(line[3:] or 0)
        elif line.startswith("FNF:"): cur["fnf"] = int(line[4:] or 0)
        elif line.startswith("FNH:"): cur["fnh"] = int(line[4:] or 0)
        elif line.startswith("BRF:"): cur["brf"] = int(line[4:] or 0)
        elif line.startswith("BRH:"): cur["brh"] = int(line[4:] or 0)
        elif line == "end_of_record":
            if cur["lf"] == 0: cur["lf"] = cur["_lf"]
            if cur["lh"] == 0: cur["lh"] = cur["_lh"]
            files.append(cur); cur = None

    def pct(h, f): return round(100.0 * h / f, 1) if f else 0.0
    for f in files:
        f["line_pct"] = pct(f["lh"], f["lf"])
        f["func_pct"] = pct(f["fnh"], f["fnf"])
        f["branch_pct"] = pct(f["brh"], f["brf"])

    lf, lh = sum(f["lf"] for f in files), sum(f["lh"] for f in files)
    fnf, fnh = sum(f["fnf"] for f in files), sum(f["fnh"] for f in files)
    brf, brh = sum(f["brf"] for f in files), sum(f["brh"] for f in files)
    summary = {"line_pct": pct(lh,lf), "func_pct": pct(fnh,fnf), "branch_pct": pct(brh,brf),
               "lines": f"{lh}/{lf}", "funcs": f"{fnh}/{fnf}", "branches": f"{brh}/{brf}"}
    return summary, sorted(files, key=lambda f: f["line_pct"])


def load_history(path: pathlib.Path) -> list[dict]:
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


# ── HTML rendering ────────────────────────────────────────────────────────────
def render_dashboard(codeql_rows, clang_rows, cov_summary, cov_files, history, timestamp) -> str:
    env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)
    env.globals["sev_colour"] = _sev_colour
    env.globals["cov_colour"] = _cov_colour
    env.globals["delta"] = _delta_badge
    env.filters["basename"] = lambda p: pathlib.Path(p).name or p
    env.tests["number"] = lambda x: isinstance(x, (int, float)) and x is not None
    tmpl = env.get_template("dashboard.html.j2")
    return tmpl.render(
        timestamp=timestamp,
        codeql_rows=codeql_rows,
        codeql_counts=Counter(r["severity"].lower() for r in codeql_rows),
        clang_rows=clang_rows,
        clang_counts=Counter(r["severity"] for r in clang_rows),
        clang_errors=sum(1 for r in clang_rows if r["severity"] == "error"),
        cov=cov_summary or None,
        cov_files=cov_files,
        history=history,
        prev=history[-2] if len(history) >= 2 else None,
    )


# ── GitHub Actions step summary ───────────────────────────────────────────────
def write_github_summary(codeql_rows, clang_rows, cov_summary, history, summary_path) -> None:
    lines = ["## Quality Dashboard\n",
             "### CodeQL (MISRA C++)\n"]
    if not codeql_rows:
        lines.append("**No findings.** :white_check_mark:\n")
    else:
        counts = Counter(r["severity"].lower() for r in codeql_rows)
        lines += [f"**Total: {len(codeql_rows)} findings**\n",
                  "| Severity | Count |", "|----------|------:|"]
        for sev in ["critical","high","error","warning","medium","low","recommendation","note"]:
            if sev in counts: lines.append(f"| {sev.capitalize()} | {counts[sev]} |")

    lines += ["", "### Clang-Tidy\n"]
    if not clang_rows:
        lines.append("**No warnings.** :white_check_mark:\n")
    else:
        counts = Counter(r["severity"] for r in clang_rows)
        lines += [f"**Total: {len(clang_rows)} warnings**\n",
                  "| Severity | Count |", "|----------|------:|"]
        for sev in ["error","warning"]:
            if sev in counts: lines.append(f"| {sev.capitalize()} | {counts[sev]} |")

    lines += ["", "### Coverage\n"]
    if cov_summary:
        lines += ["| Metric | Value |", "|--------|-------|",
                  f"| Lines | {cov_summary['line_pct']:.1f}% ({cov_summary['lines']}) |",
                  f"| Functions | {cov_summary['func_pct']:.1f}% ({cov_summary['funcs']}) |",
                  f"| Branches | {cov_summary['branch_pct']:.1f}% ({cov_summary['branches']}) |"]
    else:
        lines.append("Coverage data not available.\n")

    if len(history) >= 2:
        prev, curr = history[-2], history[-1]
        lines += ["", "### KPI Trend vs Previous Run\n",
                  "| Metric | Prev | Now | Δ |", "|--------|------|-----|---|"]
        for label, key, hib in [("CodeQL findings","codeql",False),
                                  ("Clang-Tidy warnings","clang_tidy",False),
                                  ("Line coverage %","line_cov",True),
                                  ("Branch coverage %","branch_cov",True)]:
            pv, cv = prev.get(key), curr.get(key)
            if pv is not None and cv is not None:
                diff = cv - pv
                sym = "↓" if diff < 0 else ("↑" if diff > 0 else "=")
                good = (diff < 0) if not hib else (diff > 0)
                icon = "✅" if good else ("⚠️" if diff != 0 else "")
                fmt = f"{abs(diff):.1f}" if isinstance(diff, float) else str(abs(int(diff)))
                lines.append(f"| {label} | {pv} | {cv} | {sym}{fmt} {icon} |")
        lines.append(f"\n_Tracking since {history[0].get('date','start')} ({len(history)} runs)_")

    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description="Generate unified quality dashboard")
    parser.add_argument("--csv",            default="codeql_results/codeql-results.csv")
    parser.add_argument("--clang-tidy-dir", default="bazel-bin")
    parser.add_argument("--lcov",           default="")
    parser.add_argument("--html",           default="codeql_results/dashboard.html")
    parser.add_argument("--github-summary", action="store_true")
    parser.add_argument("--history",        default="codeql_results/quality_history.json")
    parser.add_argument("--serve",          action="store_true")
    parser.add_argument("--port",           type=int, default=8080)
    args = parser.parse_args()

    _ws = pathlib.Path(os.environ.get("BUILD_WORKSPACE_DIRECTORY", pathlib.Path.cwd()))

    def _r(p): pp = pathlib.Path(p); return pp if pp.is_absolute() else _ws / pp

    csv_path       = _r(args.csv)
    clang_tidy_dir = _r(args.clang_tidy_dir)
    lcov_path      = _r(args.lcov) if args.lcov else pathlib.Path("")
    html_path      = _r(args.html)
    hist_path      = _r(args.history)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    codeql_rows            = load_codeql_csv(csv_path)
    clang_rows             = load_clang_tidy(clang_tidy_dir)
    cov_summary, cov_files = load_lcov(lcov_path)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    history = load_history(hist_path)
    history.append({"date": timestamp, "codeql": len(codeql_rows),
                    "clang_tidy": len(clang_rows),
                    "line_cov":   cov_summary.get("line_pct")   if cov_summary else None,
                    "func_cov":   cov_summary.get("func_pct")   if cov_summary else None,
                    "branch_cov": cov_summary.get("branch_pct") if cov_summary else None})
    save_history(hist_path, history)

    html_path.write_text(render_dashboard(codeql_rows, clang_rows,
                                          cov_summary, cov_files, history, timestamp),
                         encoding="utf-8")
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
        class _Q(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a): pass
        try:
            server = http.server.HTTPServer(
                ("localhost", args.port),
                lambda *a, **kw: _Q(*a, directory=str(serve_dir), **kw))
        except OSError as e:
            print(f"Cannot start server on port {args.port}: {e}", file=sys.stderr)
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

