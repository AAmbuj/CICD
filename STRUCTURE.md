CICD Project Structure Guide

This document describes the recommended project structure for easy extension and maintenance.

## Project Organization

```
CICD/
├── BUILD.bazel                 # Root build configuration
├── MODULE.bazel                # Bazel module definition
├── README.md                   # Project overview
│
├── .bazel*/                    # Bazel build outputs (gitignored)
├── bazel-bin/                  # Build artifacts (gitignored)
├── bazel-testlogs/             # Test logs (gitignored)
├── bazel-out/                  # Build outputs (gitignored)
│
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD workflows
│   └── CODEOWNERS              # Code ownership
│
├── .bazelrc                    # Bazel configuration
├── .bazelversion               # Bazel version lock
├── .clang-format               # Code formatting rules
├── .clang-tidy                 # Clang-Tidy configuration
│
├── include/                    # Public API contracts
│   └── calculator/
│       ├── i_calculator_service.h  # Service interface (mockable)
│       ├── calculator_service.h
│       ├── operations.h         # Compatibility include
│       └── operations/
│           └── arithmetic_operations.h
├── src/                        # Core implementation
│   ├── core/
│   │   └── calculator_service.cc
│   └── operations/
│       └── arithmetic_operations.cc
├── app/                        # App entry points / adapters
│   └── cli_main.cc
├── tests/                      # Unit tests against public API
│   └── unit/
│       └── calculator_service_test.cc
├── calculator.h                # Backward-compatible alias header
│
├── docs/                       # Documentation (Sphinx)
│   ├── BUILD.bazel             # Documentation build rules
│   ├── README.md               # Documentation guide
│   ├── requirements_lock.txt   # Locked versions (Bazel)
│   ├── sphinx_rules.bzl        # Custom sphinx_html rule
│   ├── sphinx/                 # Docs content package
│   │   ├── BUILD.bazel         # Source/config filegroups
│   │   ├── conf.py             # Configuration
│   │   ├── requirements.txt    # Sphinx Python deps
│   │   ├── index.rst           # Main page
│   │   ├── *.rst               # Documentation pages
│   │   ├── _static/            # Static files
│   │   └── _build/             # Built HTML (generated)
│   └── tools/                  # Tooling package
│       ├── BUILD.bazel         # Builder/server/tests
│       ├── sphinx_build.py     # Sphinx builder script
│       ├── serve.py            # Local HTTP server
│       └── check_docs.sh       # Validation script
│
├── quality/                    # Quality orchestrator package
│   ├── BUILD.bazel             # Aliases and shared config groups
│   ├── coverage.bazelrc        # Coverage configuration
│   ├── clang_tidy/             # Clang-Tidy tooling
│   │   ├── BUILD.bazel
│   │   ├── clang_tidy_wrapper.py
│   │   └── linters.bzl
│   ├── dashboard/              # Quality dashboard
│   │   ├── BUILD.bazel
│   │   ├── generate_dashboard.py
│   │   └── requirements*.txt
│   └── static_analysis/        # Security scanning
│       ├── BUILD.bazel
│       ├── codeql_lint.py
│       ├── config.yaml
│       └── static_analysis.bazelrc
│
└── scripts/                    # Utility scripts
    └── run-quality.sh          # Quality tool runner
```

## Adding New Features

### 1. Adding a New Library

1. Create source files in module-aligned directories:
   ```
   include/calculator/myfeature/
   └── my_feature.h

   src/myfeature/
   └── my_feature.cc
   ```

2. Define in BUILD.bazel:
   ```python
   cc_library(
       name = "my_feature",
      srcs = ["src/myfeature/my_feature.cc"],
      hdrs = ["include/calculator/myfeature/my_feature.h"],
      includes = ["include"],
      deps = [":calculator_core"],
   )
   ```

3. Add tests:
   ```
   tests/unit/
   └── my_feature_test.cc
   ```

4. Define test in BUILD.bazel:
   ```python
   cc_test(
       name = "my_feature_test",
         srcs = ["tests/unit/my_feature_test.cc"],
       deps = [":my_feature", "@googletest//:gtest_main"],
   )
   ```

### 2. Adding New Documentation

1. Create .rst file in docs/sphinx/:
   ```bash
   touch docs/sphinx/my_topic.rst
   ```

2. Add to toctree in docs/sphinx/index.rst:
   ```rst
   .. toctree::
       my_topic
   ```

3. Build to verify:
   ```bash
   bazel build //docs:build_docs
   ```

### 3. Adding Quality Tools

1. Create new tool in quality/:
   ```
   quality/mytool/
   ├── BUILD.bazel
   └── mytool_runner.py
   ```

2. Define Bazel target
3. Reference in quality/BUILD.bazel or root BUILD.bazel

## Build System Design

### Bazel-Only Approach

All builds use Bazel exclusively for:

- **Consistency**: Same commands work locally and in CI/CD
- **Reproducibility**: Exact same outputs every time
- **Scalability**: Works as project grows
- **Dependency Management**: Clear dependency graph
- **Caching**: Fast incremental builds
- **Testing**: Isolated test environments

### Key Bazel Concepts

**Targets**: Build outputs (libraries, binaries, tests)

```bash
bazel build //:calculator      # Binary target
bazel build //docs:build_docs  # Documentation target
bazel test //:calculator_test  # Test target
bazel run //quality:dashboard  # Quality dashboard target
bazel run //quality:static_analysis -- --target=//...  # CodeQL target
```

**Packages**: Directories with BUILD.bazel files

```
//                 # Root package
//docs/sphinx      # Documentation package
//quality/         # Quality package
```

**Rules**: Build instructions

```python
cc_library()       # C++ library
cc_binary()        # C++ executable
cc_test()          # C++ test
py_binary()        # Python script
genrule()          # Custom rule
```

## Maintainability Principles

### 1. Clear Dependencies

Keep dependency graph clear and acyclic:

```
app/cli_main.cc
   └── include/calculator/calculator_service.h
            └── include/calculator/i_calculator_service.h
            └── src/core/calculator_service.cc
                     └── include/calculator/operations/arithmetic_operations.h
                              └── src/operations/arithmetic_operations.cc
```

### 2. Logical Organization

Group related files:

```
docs/               # Documentation
quality/            # Quality tools
tools/              # Build tools
```

### 3. Minimal BUILD.bazel Files

Keep build files simple and readable:

- One target per file
- Clear visibility rules
- Explicit dependencies

### 4. Documentation as Code

Document everything:

- RST files for user docs
- Comments in code
- BUILD files are self-documenting

### 5. Automated Quality

All quality checks automated:

- Bazel tests run automatically
- Static analysis in CI/CD
- Coverage reports generated
- Documentation built on commit

## Extending the Project

### Adding a New Module

Example: Adding a Statistics module

1. Create directory:
   ```bash
   mkdir -p stats
   ```

2. Create files:
   ```
   stats/
   ├── BUILD.bazel
   ├── stats.h
   ├── stats.cc
   └── stats_test.cc
   ```

3. Define BUILD.bazel:
   ```python
   cc_library(
       name = "stats",
       srcs = ["stats.cc"],
       hdrs = ["stats.h"],
   )
   
   cc_test(
       name = "stats_test",
       srcs = ["stats_test.cc"],
       deps = [":stats", "@googletest//:gtest_main"],
   )
   ```

4. Update root BUILD.bazel to include in //:all target:
   ```python
   # In root BUILD.bazel
   test_suite(
       name = "all",
       tests = [
           ":calculator_test",
           "//stats:stats_test",
       ],
   )
   ```

### Adding a Quality Tool

Example: Adding a custom linter

1. Create tool:
   ```
   quality/mylinter/
   ├── BUILD.bazel
   └── mylinter.py
   ```

2. Define BUILD.bazel:
   ```python
   py_binary(
       name = "mylinter",
       srcs = ["mylinter.py"],
   )
   ```

3. Create Bazel configuration:
   ```
   quality/mylinter.bazelrc
   ```

4. Use in CI/CD:
   ```bash
   bazel run //quality/mylinter:mylinter -- --target=//...
   ```

## Common Commands Reference

```bash
# Building
bazel build //...              # Build all
bazel build //:calculator      # Build specific target
bazel build -c opt //...       # Optimize build

# Testing
bazel test //...               # Test all
bazel test //:calculator_test  # Test specific
bazel coverage //:calculator_test  # Generate coverage

# Documentation
bazel build //docs:build_docs  # Build docs
bazel run //docs:serve_docs    # Serve locally
bazel test //docs:...          # Test docs

# Cleaning
bazel clean                    # Clean artifacts
bazel clean --expunge          # Deep clean

# Analysis
bazel query "deps(//:calculator)"    # Show dependencies
bazel analyze-profile profile.json   # Analyze build time
```

## Best Practices

1. **Keep BUILD.bazel Simple** - Easy to understand and maintain
2. **Use Meaningful Names** - Clear target and variable names
3. **Document Decisions** - Comments explaining why
4. **Test Everything** - Each module has tests
5. **Version Control** - All configuration is versioned
6. **Reproducible Builds** - Same inputs = same outputs
7. **Fast Feedback** - Incremental builds, quick tests
8. **Explicit Dependencies** - No implicit includes
9. **Avoid Code Duplication** - Share common rules
10. **Regular Cleanup** - Remove unused files/empty placeholder directories

## Troubleshooting

### Build Issues

```bash
# Clean and rebuild
bazel clean
bazel build //...

# Show detailed output
bazel build -s //...

# Check for syntax errors
bazel query "//..."
```

### Test Failures

```bash
# Run with output
bazel test --test_output=all //:calculator_test

# Debug with GDB
bazel build -c dbg //:calculator
gdb ./bazel-bin/calculator
```

### Documentation Issues

```bash
# Check build
bazel build //docs:build_docs 2>&1 | tail -50

# Verify integrity
bazel test //docs:docs_integrity
```

## Related Documentation

- [Bazel Documentation](https://bazel.build/docs)
- [Bazel Best Practices](https://bazel.build/basics/best-practices)
- [Bazel C++ Rules](https://bazel.build/reference/be/c-cpp)
- [Bazel Python Rules](https://github.com/bazelbuild/rules_python)
