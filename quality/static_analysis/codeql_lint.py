#!/usr/bin/env python3

import argparse
import os
import pathlib
import time
import shutil
import subprocess
import sys


def run(command: list[str], cwd: pathlib.Path) -> None:
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CodeQL against Bazel targets and emit SARIF and CSV outputs.",
    )
    parser.add_argument("--target", default="//...", help="Bazel target pattern to analyze")
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
    db_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    force_rebuild_define = f"CODEQL_FORCE_REBUILD={int(time.time())}"
    build_command = (
        f"bazel --batch build --config=codeql --copt=-D{force_rebuild_define} "
        f"--cxxopt=-D{force_rebuild_define} {args.target}"
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