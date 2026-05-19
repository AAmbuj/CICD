#!/usr/bin/env bash
#
# Check documentation integrity
# Verifies that all documentation files are properly structured

set -e

DOCS_DIR="${1:-.}"

if [ -d "${DOCS_DIR}/sphinx" ]; then
    SPHINX_DIR="${DOCS_DIR}/sphinx"
elif [ -d "${DOCS_DIR}/docs/sphinx" ]; then
    # Bazel sh_test runfiles layout commonly includes docs/sphinx under the runfiles root.
    SPHINX_DIR="${DOCS_DIR}/docs/sphinx"
else
    echo "Error: Sphinx directory not found under ${DOCS_DIR}"
    exit 1
fi

if [ ! -d "$SPHINX_DIR" ]; then
    echo "Error: Sphinx directory not found: $SPHINX_DIR"
    exit 1
fi

# Check for required files
echo "Checking documentation structure..."

required_files=(
    "conf.py"
    "index.rst"
    "introduction.rst"
    "quick_start.rst"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$SPHINX_DIR/$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "Error: Missing documentation files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

# Check for RST syntax issues
echo "Checking RST syntax..."

rst_files=$(find "$SPHINX_DIR" -name "*.rst" -type f)
syntax_errors=0

for file in $rst_files; do
    if ! grep -q "^[A-Za-z]" "$file" && [ -s "$file" ]; then
        echo "  Warning: $file might have empty content"
    fi
done

if [ $syntax_errors -gt 0 ]; then
    echo "Found $syntax_errors potential syntax issues"
fi

echo "✓ Documentation structure is valid"
exit 0
