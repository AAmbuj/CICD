# CICD Project - Bazel Documentation Guide

This project uses Bazel exclusively for all builds, including documentation.
No Make, Cmake, or other build systems are used.

## Why Bazel-Only?

1. **Consistency**: Same commands locally and in CI/CD
2. **Reproducibility**: Exact same outputs every time  
3. **Scalability**: Grows with the project
4. **Simplicity**: One build system to learn
5. **Performance**: Fast incremental builds and caching
6. **Dependency Management**: Clear, explicit dependencies

## Quick Start

### Build Documentation

```bash
# Build HTML documentation
bazel build //docs:build_docs

# View in browser (cross-platform)
python3 -m webbrowser "file://$PWD/bazel-bin/docs/_build/index.html"
# Linux:   xdg-open bazel-bin/docs/_build/index.html
# macOS:   open bazel-bin/docs/_build/index.html
```

### Serve Locally (Development)

```bash
# Start local HTTP server on port 8000
bazel run //docs:serve_docs

# Then visit: http://localhost:8000
```

### Test Documentation

```bash
# Verify documentation builds without errors
bazel test //docs:test_docs_build

# Check documentation structure
bazel test //docs:docs_integrity
```

## Build Targets

The `docs/BUILD.bazel` file defines:

### :build_docs
Main target - builds HTML documentation from RST sources
```bash
bazel build //docs:build_docs
Output: bazel-bin/docs/_build/index.html
```

### :serve_docs  
Development target - serves docs on local HTTP server
```bash
bazel run //docs:serve_docs
Access: http://localhost:8000
```

### :test_docs_build
Test target - verifies docs build without errors
```bash
bazel test //docs:test_docs_build
```

### :docs_integrity
Test target - checks documentation structure
```bash
bazel test //docs:docs_integrity
```

### :docs_sources
File group - all RST/MD source files
```bash
bazel build //docs:docs_sources
```

### :docs_html
File group - built HTML output (for distribution)
```bash
bazel build //docs:docs_html
```

## Configuration Files

### MODULE.bazel
Declares Python dependencies for Sphinx:
```python
pip.parse(
    hub_name = "sphinx_deps",
    python_version = "3.11",
    requirements_lock = "//docs:requirements_lock.txt",
)
```

### docs/requirements_lock.txt
Locked Python versions for reproducible builds:
- Sphinx 7.2.6
- PyData Sphinx Theme 0.14.2
- MyST Parser 2.0.0
- Other dependencies

### docs/BUILD.bazel
Bazel rules for documentation:
- genrule to run Sphinx
- py_binary for local serving
- Tests for validation

### docs/sphinx/conf.py
Sphinx configuration:
- Project metadata
- Extensions (autodoc, napoleon, viewcode, myst_parser)
- Theme (pydata_sphinx_theme)
- HTML options

## Development Workflow

### 1. Edit Documentation

```bash
# Edit RST files
vim docs/sphinx/index.rst
vim docs/sphinx/my_page.rst
```

### 2. Build Locally

```bash
# Quick build
bazel build //docs:build_docs

# Build with output
bazel build -s //docs:build_docs 2>&1 | tail -50
```

### 3. Preview Changes

```bash
# Serve for local testing
bazel run //docs:serve_docs

# View at http://localhost:8000
# Refresh browser to see changes
```

### 4. Test Build

```bash
# Verify build succeeds without errors
bazel test //docs:test_docs_build

# Check integrity
bazel test //docs:docs_integrity
```

### 5. Commit Changes

```bash
git add docs/sphinx/my_page.rst
git commit -m "docs: add my_page documentation"
```

## Adding New Documentation Pages

### 1. Create RST File

```bash
touch docs/sphinx/my_topic.rst
```

### 2. Write Content

```rst
My Topic
========

Introduction paragraph.

Key Sections
~~~~~~~~~~~~

* Point 1
* Point 2

Code Example
~~~~~~~~~~~~

.. code-block:: python

    def example():
        pass
```

### 3. Link from Index

Edit `docs/sphinx/index.rst`:

```rst
.. toctree::
   :maxdepth: 2
   :caption: My Section:

   my_topic
```

### 4. Build and Test

```bash
bazel build //docs:build_docs
bazel test //docs:test_docs_build
```

## Customizing the Build

### Change Sphinx Options

The docs build uses the custom `sphinx_html` rule defined in `docs/sphinx_rules.bzl`,
which delegates to `docs/tools/sphinx_build.py`. To change Sphinx flags, edit the
builder script:

```python
# docs/tools/sphinx_build.py
cmd = [sphinx_build, "-b", "html", "-W", "-n", "--keep-going", src_dir, out_dir]
```

Common `sphinx-build` options:
- `-b html` - Output format
- `-W` - Treat warnings as errors
- `-n` - Nitpicky mode (warn about all references)
- `--keep-going` - Continue after individual errors

### Add Build Dependencies

In `docs/BUILD.bazel`:

```python
genrule(
    name = "build_docs",
    srcs = [
        ":docs_sources",
        ":sphinx_config",
        "//quality:coverage_badge",  # Add dependency
    ],
    # ... rest of rule
)
```

### Create Custom Sphinx Extensions

1. Create Python file: `docs/sphinx/my_extension.py`
2. Update `docs/sphinx/conf.py`:
   ```python
   extensions = [
       # ... existing
       "my_extension",
   ]
   ```
3. Update `docs/BUILD.bazel` to include as dependency

## Integration with CI/CD

### GitHub Actions Example

The project's actual Pages workflow at `.github/workflows/docs-pages.yml` uses:

```yaml
name: Docs Pages

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Bazel
        uses: bazel-contrib/setup-bazel@0.8.5
        with:
          bazelisk-cache: true
          disk-cache: ${{ github.workflow }}
          repository-cache: true

      - name: Build documentation with Bazel
        run: |
          bazel build //docs:build_docs
          rm -rf _site && mkdir -p _site
          cp -a bazel-bin/docs/_build/. _site/

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: _site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

### Local CI Check

Before pushing, run:

```bash
# Build
bazel build //docs:build_docs

# Test
bazel test //docs:test_docs_build

# Check
bazel test //docs:docs_integrity
```

## Python Dependencies

### Updating Dependencies

1. Edit `docs/requirements.txt`:
   ```
   sphinx>=7.0.0
   pydata-sphinx-theme>=0.14.0
   # Add new package
   my_package>=1.0.0
   ```

2. Regenerate lock file:
   ```bash
   bazel mod tidy
   ```

3. Bazel uses locked versions from `docs/requirements_lock.txt`

### Viewing Installed Packages

```bash
# Query Python environment
bazel query "@sphinx_deps//:*"
```

## Troubleshooting

### Documentation Build Fails

```bash
# Get full error output
bazel build //docs:build_docs 2>&1 | tail -100

# Run with verbose Bazel output
bazel build -s //docs:build_docs 2>&1 | tail -100
```

### Changes Not Appearing

```bash
# Force rebuild (no cache)
bazel clean
bazel build //docs:build_docs
```

### Local Server Not Starting

```bash
# Check if build succeeded first
bazel build //docs:build_docs

# Verify output exists
ls -la bazel-bin/docs/_build/index.html

# Run server manually
cd bazel-bin/docs/_build
python3 -m http.server 8000
```

### Python Package Issues

```bash
# Check available packages
bazel query "@sphinx_deps//:*"

# Update dependencies
bazel mod tidy
bazel sync
```

## File Structure

```
docs/
├── BUILD.bazel                 # Bazel build rules
├── README.md                   # Documentation guide
├── requirements_lock.txt       # Locked versions (Bazel uses this)
├── sphinx_rules.bzl            # Custom sphinx_html Starlark rule
├── tools/
│   ├── BUILD.bazel
│   ├── sphinx_build.py        # Sphinx builder script
│   ├── serve.py               # HTTP server for local serving
│   └── check_docs.sh          # Documentation validation
└── sphinx/
    ├── BUILD.bazel
    ├── conf.py                # Sphinx configuration
    ├── requirements.txt       # Python package list for sphinx
    ├── index.rst              # Main documentation page
    ├── introduction.rst       # Introduction
    ├── quick_start.rst        # Quick start guide
    ├── architecture.rst       # Architecture docs
    ├── building.rst           # Build instructions
    ├── testing.rst            # Testing guide
    ├── quality.rst            # Code quality docs
    ├── code_coverage.rst      # Coverage guide
    ├── development.rst        # Development guide
    ├── contributing.rst       # Contributing guide
    ├── _static/               # Static files (CSS, images)
    │   └── css/
    │       └── default_custom.css
    └── _build/                # Generated HTML (gitignored)
```

## Best Practices

1. **Build Before Committing**: Always run `bazel build //docs:build_docs`
2. **Test Locally**: Use `bazel run //docs:serve_docs` to preview
3. **Keep RST Clean**: Validate syntax before committing
4. **Document Changes**: Update relevant docs when code changes
5. **Review Output**: Check HTML for proper rendering
6. **Use Cross-References**: Link between pages with `:ref:` and `:doc:`
7. **Update Version**: Bump `conf.py` version with releases
8. **Maintain Examples**: Keep code examples current
9. **Test Links**: Verify all internal and external links work
10. **Version Control**: Commit all documentation changes

## Additional Resources

- [Bazel Documentation](https://bazel.build/docs)
- [Bazel Python Rules](https://github.com/bazelbuild/rules_python)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/)
