#!/usr/bin/env bash
#
# Run a strict Sphinx build as a Bazel test.

set -euo pipefail

CONF_PATH="${1:?Missing conf.py path}"
SPHINX_BIN="${2:?Missing sphinx builder path}"
SPHINX_DIR="$(dirname "${CONF_PATH}")"
BUILD_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "${BUILD_DIR}"
}
trap cleanup EXIT

"${SPHINX_BIN}" -b html -W "${SPHINX_DIR}" "${BUILD_DIR}"

echo "Documentation strict build passed"
