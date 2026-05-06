# CICD

Learning CI/CD pipeline for GitHub Actions with a small Bazel-based C++ project.

## Build, Test, Run

```bash
bazel build //...
bazel test //:calculator_test
bazel run //:calculator
```

## Quality Tools

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
bazel run //quality/static_analysis:codeql_lint -- --target=//...
```

To scope CodeQL to a single target:

```bash
bazel run //quality/static_analysis:codeql_lint -- --target=//:calculator
```
