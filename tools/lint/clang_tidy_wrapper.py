#!/usr/bin/env python3

import os
import pathlib
import subprocess
import sys


def find_fetched_clang_tidy() -> str | None:
    roots = []
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        roots.append(pathlib.Path(runfiles_dir))
    roots.append(pathlib.Path(sys.argv[0] + ".runfiles"))

    for root in roots:
        candidate = root / "_main~_repo_rules~clang_tidy_linux_amd64" / "file" / "downloaded"
        if candidate.exists():
            return str(candidate)
        candidate = root / "clang_tidy_linux_amd64" / "file" / "downloaded"
        if candidate.exists():
            return str(candidate)
    return None


def gcc_system_includes() -> list[str]:
    command = ["g++", "-E", "-x", "c++", "-", "-v"]
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )

    lines = completed.stdout.splitlines()
    includes = []
    collecting = False
    for line in lines:
        if line.strip() == "#include <...> search starts here:":
            collecting = True
            continue
        if collecting and line.strip() == "End of search list.":
            break
        if collecting:
            include_dir = line.strip()
            if include_dir:
                includes.append(include_dir)
    return includes


def main() -> int:
    clang_tidy = find_fetched_clang_tidy()
    if clang_tidy is None:
        print("fetched clang-tidy binary not found in Bazel runfiles", file=sys.stderr)
        return 1

    extra_args = []
    for include_dir in gcc_system_includes():
        extra_args.extend([
            "--extra-arg-before=-isystem",
            f"--extra-arg-before={include_dir}",
        ])

    command = [clang_tidy, *extra_args, *sys.argv[1:]]
    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())