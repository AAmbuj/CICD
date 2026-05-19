# CICD

Learning CI/CD pipeline for GitHub Actions with a small Bazel-based C++ project.

## Quick Start

### Build, Test, Run

```bash
# Build all targets
bazel build //...

# Run tests
bazel test //:calculator_test

# Run the application
bazel run //:calculator
```

### Documentation

Build and view the comprehensive documentation:

```bash
# Build documentation
bazel build //docs:build_docs

# View in browser
python3 -m webbrowser "file://$PWD/bazel-bin/docs/_build/index.html"

# Or serve locally
bazel run //docs:serve_docs
# Then visit http://localhost:8000
```

See [docs/README.md](docs/README.md) for complete documentation build instructions.

Linux alternative: `xdg-open bazel-bin/docs/_build/index.html`

macOS alternative: `open bazel-bin/docs/_build/index.html`

Windows PowerShell alternative: `start bazel-bin/docs/_build/index.html`

Documentation can also be published to GitHub Pages using the workflow in
`.github/workflows/docs-pages.yml`.

## Project Structure

The project is organized for easy extension and maintenance:

```
CICD/
├── include/calculator/   # Public API headers
│   ├── i_calculator_service.h          # Service interface (mockable)
│   ├── calculator_service.h
│   ├── operations.h                    # Compatibility header
│   └── operations/arithmetic_operations.h
├── src/                  # Core implementation by module
│   ├── core/calculator_service.cc
│   └── operations/arithmetic_operations.cc
├── app/                  # CLI/application entry points
├── tests/unit/           # Unit tests against public APIs
│   └── calculator_service_test.cc
├── calculator.h          # Backward-compatible header alias
├── docs/                 # Docs orchestrator package
│   ├── sphinx/           # Documentation content package
│   └── tools/            # Documentation tooling package
├── quality/              # Quality orchestrator package
│   ├── clang_tidy/       # Clang-Tidy tooling
│   ├── dashboard/        # Quality dashboard module
│   └── static_analysis/  # CodeQL static analysis module
└── scripts/              # Utility scripts
```

For detailed structure and extension guide, see [STRUCTURE.md](STRUCTURE.md).

## Bazel Build System

All builds use Bazel exclusively for consistency, reproducibility, and scalability.

Architecture-focused targets:

```bash
# Core library
bazel build //:calculator_lib

# Application layer
bazel run //:calculator

# Tests
bazel test //:calculator_test
```

### Common Commands

```bash
# Build all targets
bazel build //...

# Build specific target
bazel build //:calculator

# Run tests
bazel test //...

# Generate code coverage
bazel coverage //:calculator_test

# Clean build artifacts
bazel clean
```

### Root Target Map

Use these root aliases/suites for quick workflow discovery:

```bash
# Core architecture aliases
bazel build //:core_lib
bazel run //:core_app
bazel test //:unit_tests

# Documentation aliases
bazel build //:docs_build
bazel run //:docs_serve
bazel test //:docs_checks

# Quality aliases
bazel run //:quality_dashboard -- --help
bazel run //:quality_static_analysis -- --target=//...

# End-to-end checks for contributors
bazel test //:project_checks
```

## Quality Tools

All quality tools are integrated into the Bazel build system.

### Clang-Tidy

Run static analysis through Bazel:

```bash
bazel test --config=clang-tidy //...
```

To run on a specific target:

```bash
bazel test --config=clang-tidy //:calculator_test
```

### Coverage

Generate LCOV coverage data through Bazel:

```bash
bazel coverage //:calculator_test
```

The combined LCOV report is written to:

```bash
bazel-out/_coverage/_coverage_report.dat
```

### CodeQL

Run the Bazel CodeQL entry point:

```bash
bazel run //quality:static_analysis -- --target=//...
```

## Documentation

The project includes comprehensive Sphinx documentation covering:

- **Getting Started** - Installation and quick start guide
- **Architecture** - System design and components
- **Building** - Detailed build instructions and configuration
- **Testing** - Unit testing and test coverage
- **Quality** - Code quality tools and best practices
- **Development** - Development environment setup
- **Contributing** - How to contribute to the project

All documentation is built using Bazel for consistency with the build system.

See [docs/README.md](docs/README.md) for documentation building instructions.

## Project Organization

For detailed project structure and extension guide, see [STRUCTURE.md](STRUCTURE.md).

This document explains:

- How the project is organized
- How to add new features and modules with minimal coupling
- How to extend the documentation
- Bazel best practices
- Maintenance principles

## Architecture Principles

- Public headers in `include/` define stable interfaces.
- `ICalculatorService` provides a mockable contract; depend on it for testable composition.
- `src/core/` contains service-level business logic.
- `src/operations/` contains isolated operation modules.
- App entrypoints in `app/` only compose services and I/O.
- Tests in `tests/unit/` validate behavior through public interfaces.
- Compatibility shims (like `calculator.h`) preserve old includes while code evolves.

## Adding New Features

1. Add/extend public interfaces in `include/` (prefer module-specific subfolders).
2. Implement behavior in the matching module path under `src/`.
3. Wire service orchestration in `src/core/` only when cross-module coordination is needed.
4. Add tests in `tests/unit/` for all new functionality.
5. Update Bazel targets and deps explicitly in `BUILD.bazel`.

## Resources

- [Bazel Documentation](https://bazel.build/docs) - Official Bazel docs
- [docs/README.md](docs/README.md) - Documentation build guide
- [STRUCTURE.md](STRUCTURE.md) - Project structure and extension guide
- [.github/workflows](.github/workflows) - CI/CD configuration

To scope CodeQL to a single target:

```bash
bazel run //quality:static_analysis -- --target=//:calculator
```
