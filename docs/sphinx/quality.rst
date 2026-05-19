Code Quality
============

Quality Assurance Tools
-----------------------

The project integrates multiple tools for maintaining high code quality:

1. **Clang-Tidy** - Static analysis and linting
2. **CodeQL** - Security vulnerability scanning
3. **Code Coverage** - Test coverage measurement
4. **Compiler Warnings** - Strict compilation flags

Static Analysis with Clang-Tidy
--------------------------------

Purpose
~~~~~~~

Clang-Tidy performs static analysis to catch:

- Code style violations
- Performance issues
- Potential bugs
- Memory leaks
- Incorrect API usage

Installation
~~~~~~~~~~~~

Clang-Tidy is typically installed with LLVM:

.. code-block:: bash

    # Ubuntu/Debian
    sudo apt-get install clang-tools

    # Verify installation
    clang-tidy --version

Running Clang-Tidy
~~~~~~~~~~~~~~~~~~

Run analysis on all targets:

.. code-block:: bash

    bazel test --config=clang-tidy //...

Run on specific target:

.. code-block:: bash

    bazel test --config=clang-tidy //:calculator

View detailed output:

.. code-block:: bash

    bazel test --config=clang-tidy --test_output=all //:calculator

Configuration
~~~~~~~~~~~~~~

Clang-Tidy is configured via **.clang-tidy** file:

.. code-block:: yaml

    ---
    Checks: >
      -* ,
      readability-* ,
      performance-* ,
      bugprone-* ,
      google-* ,
      modernize-* ,
      -readability-magic-numbers ,
      -readability-function-cognitive-complexity
    WarningsAsErrors: ''
    HeaderFilterRegex: '.*'
    AnalyzeTemporaryDtors: false

Common Checks
~~~~~~~~~~~~~

**readability-*** - Code readability

- Variable names are meaningful
- Function names follow conventions
- Code structure is clear

**performance-*** - Performance issues

- Unnecessary copies
- Inefficient algorithms
- Cache-unfriendly code patterns

**bugprone-*** - Bug detection

- Uninitialized variables
- Integer overflows
- Resource leaks

**modernize-*** - Modern C++ practices

- Use ``auto`` where appropriate
- Use smart pointers
- Use range-based for loops

**google-*** - Google's style guide

- Naming conventions
- Documentation comments
- Code organization

Fixing Issues
~~~~~~~~~~~~~

Clang-Tidy can automatically fix many issues:

.. code-block:: bash

    clang-tidy -fix src/core/calculator_service.cc -- -std=c++17

CodeQL Security Scanning
------------------------

Purpose
~~~~~~~

CodeQL analyzes code for security vulnerabilities:

- SQL injection vulnerabilities
- Buffer overflows
- Use-after-free errors
- Logic errors in security-critical code

Setup
~~~~~

CodeQL is configured in **quality/static_analysis/codeql_lint.py**:

.. code-block:: python

    import subprocess
    import argparse

    def run_codeql_analysis(target):
        """Run CodeQL analysis on target"""
        cmd = [
            "codeql", "database", "create",
            "--language=cpp",
            "--source-root=.",
        ]
        subprocess.run(cmd, check=True)

Running CodeQL
~~~~~~~~~~~~~~

Run CodeQL analysis:

.. code-block:: bash

    bazel run //quality/static_analysis:codeql_lint -- --target=//...

View results:

.. code-block:: bash

    # Results are in SARIF format
    find . -name "*.sarif" -exec cat {} \;

Integration with GitHub
~~~~~~~~~~~~~~~~~~~~~~~

CodeQL runs automatically on each push and pull request:

**Workflow**: `.github/workflows/codeql.yml`

- Builds the project
- Runs CodeQL analysis
- Uploads results to GitHub Code Scanning tab
- Shows security alerts in the UI

View results:

1. Go to repository settings
2. Security → Code Scanning Alerts
3. Review findings

Code Coverage
-------------

Purpose
~~~~~~~

Code coverage measures what percentage of code is exercised by tests:

- Identifies untested code
- Helps prioritize new tests
- Tracks quality improvements over time

Measuring Coverage
~~~~~~~~~~~~~~~~~~

Generate LCOV coverage report:

.. code-block:: bash

    bazel coverage //:calculator_test

Generate combined coverage:

.. code-block:: bash

    bazel coverage --combined_report=lcov //:calculator_test

The report is saved to:

.. code-block:: bash

    bazel-out/_coverage/_coverage_report.dat

Viewing Coverage Reports
~~~~~~~~~~~~~~~~~~~~~~~~

Convert to HTML for interactive viewing:

.. code-block:: bash

    # Generate coverage
    bazel coverage //:calculator_test

    # Convert LCOV to HTML
    genhtml bazel-out/_coverage/_coverage_report.dat \
        -o coverage_html

    # Open in browser
    open coverage_html/index.html

View summary:

.. code-block:: bash

    lcov --summary bazel-out/_coverage/_coverage_report.dat

Expected output:

.. code-block:: text

    lines.......: 95.3% ( 175 of 184 lines )
    functions..: 100.0% ( 25 of 25 functions )
    branches...: 88.2% ( 45 of 51 branches )

Configuration
~~~~~~~~~~~~~

Configure coverage in **quality/coverage.bazelrc**:

.. code-block:: bash

    coverage --instrumentation_filter="//..."
    coverage --java_runtime_version=local
    coverage --combined_report=lcov

Compiler Warnings
-----------------

Strict Compilation Flags
~~~~~~~~~~~~~~~~~~~~~~~~

The project uses strict compiler flags to catch issues early:

.. code-block:: bash

    # In .bazelrc
    build --cxxopt='-Wall'      # All warnings
    build --cxxopt='-Wextra'    # Extra warnings
    build --cxxopt='-Wpedantic' # Pedantic warnings
    build --cxxopt='-Werror'    # Treat warnings as errors

Important Warning Flags
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    -Wall           # Enable all common warnings
    -Wextra         # Enable extra warnings
    -Wpedantic      # Strict ISO compliance
    -Wshadow        # Variable shadowing
    -Wnull-dereference  # Potential null dereferences
    -Wdouble-promotion  # Implicit double promotions
    -Wformat=2      # Format string security

Treating Warnings as Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    build --cxxopt='-Werror'

This forces developers to fix all warnings before code is accepted.

Code Formatting
---------------

Clang-Format Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure in **.clang-format**:

.. code-block:: yaml

    Language: Cpp
    BasedOnStyle: Google
    ColumnLimit: 100
    IndentWidth: 4
    UseTab: Never
    AllowShortFunctionsOnASingleLine: None

Formatting Code
~~~~~~~~~~~~~~~

Format a single file:

.. code-block:: bash

    clang-format -i src/core/calculator_service.cc

Format all C++ files:

.. code-block:: bash

    find . -name "*.cc" -o -name "*.h" | xargs clang-format -i

Check formatting without modifying:

.. code-block:: bash

    clang-format --dry-run src/core/calculator_service.cc

Integrating with Bazel
~~~~~~~~~~~~~~~~~~~~~~

Format check in CI:

.. code-block:: bash

    # Check formatting
    bazel run //:format_check

    # Auto-format
    bazel run //:format

CI/CD Quality Gates
-------------------

Automated Quality Checks
~~~~~~~~~~~~~~~~~~~~~~~~

GitHub Actions automatically runs:

1. **Build Verification** - Code compiles without errors
2. **Test Execution** - All tests pass
3. **Static Analysis** - Clang-Tidy checks pass
4. **Security Scanning** - CodeQL finds no new issues
5. **Code Coverage** - Coverage meets minimum threshold

Workflow Files
~~~~~~~~~~~~~~

- `.github/workflows/build_test.yml` - Builds and tests
- `.github/workflows/codeql.yml` - Security scanning

Status Checks
~~~~~~~~~~~~~

Pull requests must pass all checks:

.. code-block:: text

    ✓ build (Build the project)
    ✓ test (Run tests)
    ✓ coverage (Generate coverage report)
    ✓ quality (Clang-Tidy checks)
    ✓ codeql (Security scan)

Quality Metrics Dashboard
--------------------------

Coverage Dashboard
~~~~~~~~~~~~~~~~~~

Location: **quality/dashboard/generate_dashboard.py**

Generates an HTML dashboard showing:

- Code coverage trends
- Test pass rates
- Build times
- Quality metrics

Generate dashboard:

.. code-block:: bash

    bazel run //quality/dashboard:generate_dashboard

Open in browser:

.. code-block:: bash

    open quality/dashboard/index.html

Monitoring Metrics
~~~~~~~~~~~~~~~~~~

Track over time:

- Line coverage percentage
- Branch coverage percentage
- Number of quality issues
- Test execution time
- Build duration

Set Quality Thresholds
~~~~~~~~~~~~~~~~~~~~~~

Define minimum acceptable quality levels:

.. code-block:: yaml

    quality:
      coverage:
        line: 80      # Minimum 80% line coverage
        branch: 75    # Minimum 75% branch coverage
      static_analysis:
        critical: 0   # Zero critical issues
        high: 5       # Max 5 high-severity issues

Quality Improvement Strategy
-----------------------------

1. **Establish Baseline** - Measure current quality metrics
2. **Set Goals** - Define target metrics (e.g., 85% coverage)
3. **Implement Tools** - Integrate quality tools in CI/CD
4. **Monitor Progress** - Track metrics over time
5. **Iterate** - Continuously improve based on results
6. **Educate Team** - Share quality practices and patterns

Best Practices
--------------

1. **Code Review** - Have peers review all code changes
2. **Early Testing** - Write tests as you code
3. **Coverage Goals** - Aim for 80%+ coverage
4. **Fix Issues Early** - Address quality issues immediately
5. **Automate Checks** - Use CI/CD for enforcement
6. **Maintain High Standards** - Don't lower quality thresholds
7. **Learn from Failures** - Analyze quality issues to prevent recurrence
8. **Document Decisions** - Record why quality rules exist
