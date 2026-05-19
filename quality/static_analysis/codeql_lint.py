#!/usr/bin/env python3

import argparse
import os
import pathlib
import time
import shutil
import subprocess
import sys


DEFAULT_EXCLUDED_TARGETS = (
    "-//:calculator_test",
)


def run(command: list[str], cwd: pathlib.Path) -> None:
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def query_stdout(command: list[str], cwd: pathlib.Path) -> str:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        raise SystemExit(completed.returncode)
    return completed.stdout


def find_codeql_binary() -> str | None:
    roots = []
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        roots.append(pathlib.Path(runfiles_dir))
    roots.append(pathlib.Path(sys.argv[0] + ".runfiles"))
    roots.append(pathlib.Path(__file__).resolve())

    seen = set()
    for root in roots:
        for candidate_root in [root, *root.parents]:
            if candidate_root in seen or not candidate_root.exists():
                continue
            seen.add(candidate_root)
            direct = candidate_root / "_main~_repo_rules~codeql_bundle_linux64" / "codeql"
            if direct.exists():
                return str(direct)
            direct = candidate_root / "codeql_bundle_linux64" / "codeql"
            if direct.exists():
                return str(direct)
            matches = list(candidate_root.glob("*_repo_rules~codeql_bundle_linux64/codeql"))
            if matches:
                return str(matches[0])
    return shutil.which("codeql")


def build_target_expression(target: str, include_tests: bool, cwd: pathlib.Path) -> str:
    if include_tests:
        return target

    target_patterns = target.split()
    positive_patterns = [pattern for pattern in target_patterns if not pattern.startswith("-")]
    negative_patterns = [pattern[1:] for pattern in target_patterns if pattern.startswith("-")]

    if not positive_patterns:
        print("At least one positive Bazel target pattern is required.", file=sys.stderr)
        raise SystemExit(1)

    base_query = f"set({' '.join(positive_patterns)})"
    filtered_query = base_query
    if negative_patterns:
        filtered_query = f"({filtered_query}) except set({' '.join(negative_patterns)})"

    for pattern in DEFAULT_EXCLUDED_TARGETS:
        excluded_target = pattern[1:] if pattern.startswith("-") else pattern
        if excluded_target not in negative_patterns:
            filtered_query = f"({filtered_query}) except set({excluded_target})"

    cpp_query = f'kind("cc_(binary|library) rule", {filtered_query})'
    resolved_targets = [
        line.strip()
        for line in query_stdout(["bazel", "query", cpp_query], cwd).splitlines()
        if line.strip()
    ]

    if not resolved_targets:
        print("No non-test C++ build targets matched the requested CodeQL scope.", file=sys.stderr)
        raise SystemExit(1)

    return " ".join(resolved_targets)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CodeQL against Bazel targets and emit SARIF and CSV outputs.",
    )
    parser.add_argument("--target", default="//...", help="Bazel target pattern to analyze")
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test targets in the CodeQL database build.",
    )
    parser.add_argument(
        "--db",
        default="codeql_db",
        help="Directory for the generated CodeQL database",
    )
    parser.add_argument(
        "--output-dir",
        default="codeql_results",
        help="Directory for analysis results",
    )
    args = parser.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parents[2]
    codeql = find_codeql_binary()
    if codeql is None:
        print("codeql binary not found in Bazel runfiles or PATH", file=sys.stderr)
        return 1

    db_dir = repo_root / args.db
    out_dir = repo_root / args.output_dir
    if db_dir.exists():
        shutil.rmtree(db_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    force_rebuild_define = f"CODEQL_FORCE_REBUILD={int(time.time())}"
    target_expression = build_target_expression(args.target, args.include_tests, repo_root)
    build_command = (
        f"bazel --batch build --config=codeql --copt=-D{force_rebuild_define} "
        f"--cxxopt=-D{force_rebuild_define} {target_expression}"
    )
    run(
        [
            codeql,
            "database",
            "create",
            str(db_dir),
            "--language=cpp",
            f"--command={build_command}",
            "--overwrite",
        ],
        repo_root,
    )

    sarif_output = out_dir / "codeql-results.sarif"
    csv_output = out_dir / "codeql-results.csv"
    query_pack = "codeql/misra-cpp-coding-standards"

    # Download the MISRA pack if it is not already present in the CodeQL bundle.
    run([codeql, "pack", "download", query_pack], repo_root)

    run(
        [
            codeql,
            "database",
            "analyze",
            str(db_dir),
            query_pack,
            "--format=sarif-latest",
            f"--output={sarif_output}",
        ],
        repo_root,
    )
    run(
        [
            codeql,
            "database",
            "analyze",
            str(db_dir),
            query_pack,
            "--format=csv",
            f"--output={csv_output}",
        ],
        repo_root,
    )

    print(f"SARIF: {sarif_output}")
    print(f"CSV:   {csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())