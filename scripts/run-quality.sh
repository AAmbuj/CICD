#!/usr/bin/env bash
# Run all quality checks locally and open the dashboard in your browser.
#
# Usage:
#   ./scripts/run-quality.sh            # run everything + open browser
#   ./scripts/run-quality.sh --no-serve # run everything, skip browser
#   ./scripts/run-quality.sh --best-effort # continue despite quality check failures

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

SERVE=true
BEST_EFFORT=false
for arg in "$@"; do
  case "$arg" in
    --no-serve)
      SERVE=false
      ;;
    --best-effort)
      BEST_EFFORT=true
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [--no-serve] [--best-effort]" >&2
      exit 2
      ;;
  esac
done

run_check() {
  local label="$1"
  shift
  echo "==> ${label}"
  if "$@"; then
    return 0
  fi

  if [[ "$BEST_EFFORT" == "true" ]]; then
    echo "Warning: ${label} failed (continuing due to --best-effort)." >&2
    return 0
  fi

  echo "Error: ${label} failed." >&2
  exit 1
}

run_check "Clang-Tidy" bazel test --config=clang-tidy //quality:Clang-tidy

run_check "CodeQL" bazel run //quality:CodeQL -- --target=//...

run_check "Coverage" bazel coverage //quality:Coverage

echo "==> Collecting results"
mkdir -p clang_tidy_results coverage_results
find bazel-bin -name "*.AspectRulesLintClangTidy.report" \
  -exec cp {} clang_tidy_results/ \; 2>/dev/null || true
REPORT="$(bazel info output_path)/_coverage/_coverage_report.dat"
if [[ -f "$REPORT" ]]; then
  cp "$REPORT" coverage_results/coverage.dat
elif [[ "$BEST_EFFORT" == "true" ]]; then
  echo "Warning: coverage report not found at $REPORT (continuing due to --best-effort)." >&2
else
  echo "Error: coverage report not found at $REPORT" >&2
  exit 1
fi

echo "==> Generating dashboard"
EXTRA_ARGS=()
$SERVE && EXTRA_ARGS=(--serve)
bazel run //quality:dashboard -- \
  --csv            codeql_results/codeql-results.csv \
  --clang-tidy-dir clang_tidy_results \
  --lcov           coverage_results/coverage.dat \
  --html           codeql_results/dashboard.html \
  "${EXTRA_ARGS[@]}"
