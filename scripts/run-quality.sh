#!/usr/bin/env bash
# Run all quality checks locally and open the dashboard in your browser.
#
# Usage:
#   ./scripts/run-quality.sh            # run everything + open browser
#   ./scripts/run-quality.sh --no-serve # run everything, skip browser

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

SERVE=true
[[ "${1:-}" == "--no-serve" ]] && SERVE=false

echo "==> Clang-Tidy"
bazel test --config=clang-tidy //... || true

echo "==> CodeQL"
bazel run //quality/static_analysis:codeql_lint -- --target=//... || true

echo "==> Coverage"
bazel coverage //:calculator_test || true

echo "==> Collecting results"
mkdir -p clang_tidy_results coverage_results
find bazel-bin -name "*.AspectRulesLintClangTidy.report" \
  -exec cp {} clang_tidy_results/ \; 2>/dev/null || true
REPORT="$(bazel info output_path)/_coverage/_coverage_report.dat"
[ -f "$REPORT" ] && cp "$REPORT" coverage_results/coverage.dat || true

echo "==> Generating dashboard"
EXTRA_ARGS=""
$SERVE && EXTRA_ARGS="--serve"
bazel run //quality/dashboard:generate_dashboard -- \
  --csv            codeql_results/codeql-results.csv \
  --clang-tidy-dir clang_tidy_results \
  --lcov           coverage_results/coverage.dat \
  --html           codeql_results/dashboard.html \
  $EXTRA_ARGS
