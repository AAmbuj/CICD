# CICD Project Documentation

This directory contains the Sphinx documentation for the CICD Project.

All documentation builds are managed through **Bazel** for consistency, reproducibility, and ease of extension.

## Quick Start

### Prerequisites

- Bazel 7.x or later
- Python 3.11+

### Build Documentation

Build HTML documentation using Bazel:

```bash
bazel build //docs:build_docs
```

View the built documentation:

```bash
python3 -m webbrowser "file://$PWD/bazel-bin/docs/_build/index.html"
```

Platform-specific alternatives:

- Linux: `xdg-open bazel-bin/docs/_build/index.html`
- macOS: `open bazel-bin/docs/_build/index.html`
- Windows PowerShell: `start bazel-bin/docs/_build/index.html`

### Serve Documentation Locally

For development and testing, serve documentation on a local HTTP server:

```bash
bazel run //docs:serve_docs
```

Then open: **http://localhost:8000**

### Test Documentation Build

Verify documentation builds without errors:

```bash
bazel test //docs:test_docs_build
```

Check documentation structure and integrity:

```bash
bazel test //docs:docs_integrity
```

## Deploy to GitHub Pages

This repository includes an automated GitHub Pages workflow at
`.github/workflows/docs-pages.yml`.

Deployment behavior:

- Triggered automatically on every push to `main`
- Runs nightly (`0 2 * * *`) to refresh dashboard metrics
- Can also be triggered manually from the Actions tab
- Builds Sphinx HTML and a quality dashboard page
- Publishes both under the same GitHub Pages site

Standard deployment rule:

- Only `.github/workflows/docs-pages.yml` deploys GitHub Pages
- Other workflows may run checks, but they do not publish pages

Published paths on the same site:

- `/` -> Sphinx documentation
- `/dashboard/` -> Quality dashboard

### One-time Repository Setup

1. Open **Settings → Pages** in the GitHub repository.
2. Set **Source** to **GitHub Actions**.
3. Save and run the **Docs Pages** workflow (or push a docs change).

After the first successful deployment, your site URL appears in the workflow
summary and in the Pages settings.

## Project Structure

```
docs/
├── BUILD.bazel              # Orchestrator package targets
├── sphinx/                  # Documentation content package
│   ├── BUILD.bazel         # Source/config filegroups
│   ├── conf.py             # Sphinx configuration
│   ├── index.rst           # Main documentation page
│   ├── introduction.rst     # Project introduction
│   ├── quick_start.rst     # Quick start guide
│   ├── architecture.rst     # Architecture documentation
│   ├── building.rst        # Build instructions
│   ├── testing.rst         # Testing guide
│   ├── quality.rst         # Code quality tools
│   ├── code_coverage.rst   # Code coverage guide
│   ├── development.rst     # Development guide
│   ├── contributing.rst    # Contributing guidelines
│   ├── _static/            # Static files (CSS, images)
│   ├── _build/             # Built HTML (generated)
│   └── requirements.txt    # Package dependencies
│
├── tools/                  # Documentation tooling package
│   ├── BUILD.bazel         # Tool/test executable targets
│   ├── serve.py           # HTTP server for local serving
│   └── check_docs.sh      # Documentation integrity checker
├── requirements_lock.txt  # Locked Python dependencies for reproducibility
└── README.md              # This file
```

## Building and Extending

### Build Targets

The `docs/BUILD.bazel` file exposes contributor-facing targets:

| Target | Purpose |
|--------|---------|
| `//docs:build_docs` | Build HTML documentation from RST sources |
| `//docs:serve_docs` | Serve documentation locally for development |
| `//docs:test_docs_build` | Verify documentation builds without errors |
| `//docs:docs_integrity` | Check documentation structure validity |
| `//docs:docs_sources` | Filegroup of all documentation source files |
| `//docs:sphinx_config` | Sphinx configuration files |
| `//docs:docs_html` | Output documentation for distribution |

Internal implementation targets now live in subpackages:

- `//docs/sphinx:*` for source/config groups
- `//docs/tools:*` for builder, serving, and test executables

### Adding New Documentation Pages

1. **Create a new `.rst` file** in `docs/sphinx/`:

   ```bash
   touch docs/sphinx/my_new_page.rst
   ```

2. **Write content** using reStructuredText format:

   ```rst
   My New Page
   ===========

   This is my documentation page.

   Key Features
   -----------

   * Feature 1
   * Feature 2
   ```

3. **Link from index.rst** to make it discoverable:

   ```rst
   .. toctree::
      :maxdepth: 2
      :caption: My Section:

      my_new_page
   ```

4. **Build to verify**:

   ```bash
   bazel build //docs:build_docs
   bazel run //docs:serve_docs
   ```

### Customizing Build Behavior

The documentation build uses the custom `sphinx_html` Starlark rule defined in
`docs/sphinx_rules.bzl`, which invokes `docs/tools/sphinx_build.py`.

To change Sphinx flags (e.g. add `-n` for nitpicky mode), edit the builder script:

```python
# docs/tools/sphinx_build.py
cmd = [sphinx_build, "-b", "html", "-W", "-n", "--keep-going", src_dir, out_dir]
```

To add new output targets or integrate other build steps, extend `docs/BUILD.bazel`
using the existing `sphinx_html` rule or add a new `genrule` that depends on
`:build_docs` as an input.

## Bazel Integration

### Dependencies

Documentation dependencies are defined in:

- **`MODULE.bazel`** - Declares Python packages needed for Sphinx
- **`docs/requirements_lock.txt`** - Locked versions for reproducible builds

To update dependencies:

```bash
# Update MODULE.bazel with new package
# Then run:
bazel mod tidy
```

### Build Configuration

The documentation build is fully integrated with the Bazel build system:

```bash
# Build entire project including docs
bazel build //...

# Run all tests including doc validation
bazel test //...

# Build with specific configuration
bazel build -c opt //docs:build_docs
```

## Documentation Format

The documentation uses **reStructuredText** (RST) format with **Sphinx**.

### Common RST Syntax

**Headings**

```rst
Main Title
==========

Subtitle
--------

Subsubtitle
~~~~~~~~~~~
```

**Code blocks**

````rst
.. code-block:: python

    def hello():
        print("Hello, World!")

.. code-block:: bash

    bazel build //...
```

**Lists**

```rst
* Bullet point 1
* Bullet point 2
  * Nested point

1. Numbered item 1
2. Numbered item 2
```

**Admonitions**

```rst
.. note::

   This is a note.

.. warning::

   This is a warning.

.. tip::

   This is a helpful tip.
```

**Links**

```rst
`Link Text <https://example.com>`_

.. _internal-link:

Referencing: :ref:`internal-link`
```

### Sphinx Extensions

The documentation uses these Sphinx extensions:

- **sphinx.ext.autodoc** - Auto-generate docs from docstrings
- **sphinx.ext.napoleon** - Support Google/NumPy style docstrings
- **sphinx.ext.viewcode** - Add links to source code
- **myst_parser** - Support Markdown files
- **pydata_sphinx_theme** - Professional modern theme

See `docs/sphinx/conf.py` for full configuration.

## Styling and Customization

Custom CSS is in `docs/sphinx/_static/css/default_custom.css`:

```css
/* Override theme colors */
:root {
    --color-primary: #007bff;
    --color-secondary: #6c757d;
}

/* Custom styling for code blocks */
code {
    background-color: #f4f4f4;
    padding: 2px 4px;
    border-radius: 3px;
}
```

Modify this file to change documentation appearance.

## Continuous Integration

### GitHub Actions

Documentation can be built automatically in CI/CD:

```yaml
name: Build Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Bazel
        uses: bazel-contrib/setup-bazel@v0
      
      - name: Build documentation
        run: bazel build //docs:build_docs
      
      - name: Test documentation
        run: bazel test //docs:...
```

### Local Testing Before Commit

Before pushing documentation changes:

```bash
# Verify it builds
bazel build //docs:build_docs

# Check for issues
bazel test //docs:test_docs_build

# Serve locally and verify
bazel run //docs:serve_docs
```

## Best Practices

1. **Keep documentation current** - Update docs when code changes
2. **Use clear examples** - Include code examples for complex topics
3. **Follow RST conventions** - Use consistent formatting
4. **Test builds locally** - Always verify docs build without errors
5. **Link between pages** - Use cross-references for navigation
6. **Review before committing** - Have peers review doc changes
7. **Keep it simple** - Avoid overly complex explanations
8. **Document as you code** - Don't leave documentation for later
9. **Use consistent styling** - Follow the CSS style guide
10. **Update versioning** - Keep version numbers in sync

## Troubleshooting

### Problem: "Python or Sphinx not found"

**Solution**: Let Bazel manage dependencies

```bash
bazel clean --expunge
bazel build //docs:build_docs
```

### Problem: "Documentation build fails"

**Solution**: Check the error output

```bash
bazel build //docs:build_docs 2>&1 | tail -50
```

Then check the specific `.rst` file for syntax errors.

### Problem: "Changes not appearing"

**Solution**: Clean and rebuild

```bash
bazel clean //docs
bazel build //docs:build_docs
```

### Problem: "Local serve doesn't work"

**Solution**: Check if Bazel build succeeded first

```bash
bazel build //docs:build_docs
bazel run //docs:serve_docs
```

If still having issues, manually run:

```bash
python3 -m http.server 8000 --directory bazel-bin/docs/_build
```

## Deployment

### Local Deployment

Copy built documentation to a web server:

```bash
cp -r bazel-bin/docs/_build/* /var/www/docs/
```

### GitHub Pages Deployment

Use Bazel with GitHub Actions:

```yaml
- name: Build Documentation
  run: bazel build //docs:build_docs

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./bazel-bin/docs/_build
```

## Additional Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Bazel Documentation](https://bazel.build/docs)
- [Bazel Python Rules](https://github.com/bazelbuild/rules_python)
- [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/)

## License

The documentation is licensed under the Apache License 2.0. See the main LICENSE file.

