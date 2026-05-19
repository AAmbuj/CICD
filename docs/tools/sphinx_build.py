#!/usr/bin/env python3
"""Run Sphinx using Bazel-managed Python dependencies."""

import sys

from sphinx.cmd.build import main as sphinx_main


if __name__ == "__main__":
    sys.exit(sphinx_main(sys.argv[1:]))
