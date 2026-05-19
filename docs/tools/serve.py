#!/usr/bin/env python3
"""Prepare and serve a local documentation preview with dashboard data."""

import argparse
import http.server
import os
from pathlib import Path
import shutil
import socketserver
import subprocess
import sys
import tempfile


def _prepare_preview_site(
    docs_dir: Path,
    dashboard_builder: Path | None,
    workspace_root: Path | None,
) -> Path:
    preview_root = Path(tempfile.mkdtemp(prefix="cicd-docs-preview-")) / "site"
    shutil.copytree(docs_dir, preview_root)

    if dashboard_builder is None or workspace_root is None:
        return preview_root

    history_path = preview_root / "dashboard" / "quality_history.json"
    html_path = preview_root / "dashboard" / "index.html"
    codeql_csv = workspace_root / "codeql_results" / "codeql-results.csv"
    clang_tidy_dir = workspace_root / "bazel-bin"

    coverage_path = ""
    try:
        output_path = subprocess.run(
            ["bazel", "info", "output_path"],
            check=True,
            cwd=workspace_root,
            capture_output=True,
            text=True,
        ).stdout.strip()
        candidate = Path(output_path) / "_coverage" / "_coverage_report.dat"
        if candidate.is_file():
            coverage_path = str(candidate)
    except (OSError, subprocess.CalledProcessError):
        coverage_path = ""

    command = [
        str(dashboard_builder),
        "--csv",
        str(codeql_csv),
        "--clang-tidy-dir",
        str(clang_tidy_dir),
        "--html",
        str(html_path),
        "--history",
        str(history_path),
    ]
    if coverage_path:
        command.extend(["--lcov", coverage_path])

    env = os.environ.copy()
    env["BUILD_WORKSPACE_DIRECTORY"] = str(workspace_root)

    try:
        subprocess.run(
            command,
            check=True,
            cwd=workspace_root,
            env=env,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Warning: dashboard preview generation failed: {error}", file=sys.stderr)

    return preview_root


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve a local docs preview with a generated dashboard.",
    )
    parser.add_argument("docs_build_dir")
    parser.add_argument("dashboard_builder", nargs="?")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    docs_dir = Path(args.docs_build_dir)
    if not docs_dir.is_dir():
        print(f"Error: Documentation directory not found: {docs_dir}")
        return 1

    workspace_root_env = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    workspace_root = Path(workspace_root_env) if workspace_root_env else None
    dashboard_builder = Path(args.dashboard_builder) if args.dashboard_builder else None

    preview_dir = _prepare_preview_site(docs_dir, dashboard_builder, workspace_root)
    print(f"Prepared preview site at: {preview_dir}")

    if args.prepare_only:
        return 0

    os.chdir(preview_dir)
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Serving documentation at http://localhost:{args.port}")
        print(f"Directory: {preview_dir}")
        print("Press Ctrl+C to stop")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
