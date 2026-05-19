Code Coverage
==============

Code Coverage Overview
----------------------

Code coverage measures how much of your source code is executed by tests.

**Benefits**:

- Identify untested code paths
- Increase confidence in test suite
- Detect dead code
- Improve code quality
- Track quality trends over time

Coverage Metrics
----------------

Types of Coverage
~~~~~~~~~~~~~~~~~~

**Line Coverage** - % of executable lines executed by tests

- Line 1: covered (10 tests run this line)
- Line 2: not covered (0 tests run this line)
- Result: 50% line coverage

**Branch Coverage** - % of conditional branches executed

- ``if (x > 0) { ... }`` has true and false branches
- If tests only cover true branch: 50% branch coverage
- If tests cover both: 100% branch coverage

**Function Coverage** - % of functions called

- Identifies dead code functions
- Useful for API coverage

**Statement Coverage** - % of statements executed

- Similar to line coverage
- More granular than line-based

Generating Coverage Reports
-----------------------------

Generate LCOV Report
~~~~~~~~~~~~~~~~~~~~

Generate coverage for a test:

.. code-block:: bash

    bazel coverage //:calculator_test

This produces:

.. code-block:: bash

    bazel-out/_coverage/_coverage_report.dat

Combine Multiple Test Coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine coverage from multiple tests:

.. code-block:: bash

    bazel coverage --combined_report=lcov //:calculator_test //...

Generates combined report:

.. code-block:: bash

    bazel-out/_coverage/_coverage_report.dat

Viewing Coverage Reports
------------------------

View Summary Statistics
~~~~~~~~~~~~~~~~~~~~~~~

Display coverage summary:

.. code-block:: bash

    lcov --summary bazel-out/_coverage/_coverage_report.dat

Example output:

.. code-block:: text

    lines.......: 95.3% ( 175 of 184 lines )
    functions..: 100.0% ( 25 of 25 functions )
    branches...: 88.2% ( 45 of 51 branches )

Generate HTML Report
~~~~~~~~~~~~~~~~~~~~

Convert LCOV to interactive HTML:

.. code-block:: bash

    # Generate coverage
    bazel coverage //:calculator_test

    # Convert to HTML
    genhtml bazel-out/_coverage/_coverage_report.dat \
        -o coverage_html

    # Open in browser
    open coverage_html/index.html

HTML Report Contents
~~~~~~~~~~~~~~~~~~~~

The HTML report shows:

- **Summary** - Overall coverage statistics
- **Files** - Coverage per source file
- **Lines** - Covered/uncovered lines with hit count
- **Trends** - Coverage trends over time

Files are color-coded:

- **Red** - Uncovered code (0%)
- **Yellow** - Partially covered (1-99%)
- **Green** - Covered (100%)

Filtering Coverage Results
---------------------------

Coverage for Specific Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate report for specific files:

.. code-block:: bash

    bazel coverage //:calculator_test
    lcov --extract bazel-out/_coverage/_coverage_report.dat \
        "*/src/core/calculator_service.cc" -o calculator_coverage.dat
    genhtml calculator_coverage.dat -o coverage_html

Exclude Files from Coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In BUILD.bazel:

.. code-block:: bazel

    cc_test(
        name = "calculator_test",
        srcs = ["tests/unit/calculator_service_test.cc"],
        deps = [":calculator", "@google_test//:gtest_main"],
        instrumentation_filter = "//...",
        # Exclude test files from coverage
        # Only count library code coverage
    )

Coverage Configuration
----------------------

Bazel Coverage Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure in **.bazelrc** or **quality/coverage.bazelrc**:

.. code-block:: bash

    # Enable coverage instrumentation
    coverage --instrumentation_filter="//..."

    # Generate LCOV format
    coverage --combined_report=lcov

    # Coverage output path
    coverage --coverage_report_generator="@bazel_tools//tools/coverage:coverage_report_generator"

Filtering Coverage
~~~~~~~~~~~~~~~~~~

Include only specific targets:

.. code-block:: bash

    coverage --instrumentation_filter="//src/..." //:calculator_test

Exclude test files:

.. code-block:: bash

    coverage --instrumentation_filter="-//test/..." //:calculator_test

Improving Code Coverage
------------------------

Identify Uncovered Code
~~~~~~~~~~~~~~~~~~~~~~~

1. Generate HTML report
2. Open in browser
3. Look for red (uncovered) lines
4. Review why code isn't covered

Examples to test:

.. code-block:: cpp

    // Uncovered: divide by zero error path
    if (divisor == 0) {
        throw std::invalid_argument("Division by zero");
    }

Adding Tests
~~~~~~~~~~~~

Write tests for uncovered code:

.. code-block:: cpp

    TEST(CalculatorTest, DivideByZeroThrows) {
        Calculator calc;
        calc.SetOperands(10, 0);
        EXPECT_THROW(calc.Divide(), std::invalid_argument);
    }

Coverage Goals
~~~~~~~~~~~~~~

Set targets for your project:

- **Minimum**: 70% line coverage
- **Good**: 80% line coverage
- **Excellent**: 90%+ line coverage
- **Full**: 100% line coverage (rarely achieved)

Pragmatic approach:

- Core business logic: 90%+
- Utilities: 80%+
- Auto-generated code: 0% (exclude from coverage)

Coverage in CI/CD
-----------------

GitHub Actions Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Workflow: `.github/workflows/build_test.yml`

.. code-block:: yaml

    - name: Generate Coverage
      run: bazel coverage --combined_report=lcov //:calculator_test

    - name: Upload Coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./bazel-out/_coverage/_coverage_report.dat
        flags: unittests
        name: codecov-umbrella

Generate coverage report:

.. code-block:: bash

    bazel coverage --combined_report=lcov //:calculator_test

Upload to service (e.g., Codecov):

.. code-block:: bash

    curl -X POST https://codecov.io/upload/v4 \
        -H "Content-Type: multipart/form-data" \
        -F "file=@bazel-out/_coverage/_coverage_report.dat"

Enforce Minimum Coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Script to check coverage threshold:

.. code-block:: bash

    #!/bin/bash
    THRESHOLD=80
    COVERAGE=$(lcov --summary bazel-out/_coverage/_coverage_report.dat | \
        grep lines | grep -oP '\d+\.\d+(?=%)')
    
    if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
        echo "Coverage $COVERAGE% below threshold $THRESHOLD%"
        exit 1
    fi

Coverage Reporting Services
----------------------------

Codecov
~~~~~~~

Upload coverage reports to Codecov:

1. Sign up at codecov.io
2. Connect GitHub repository
3. Upload reports from CI/CD

Adds:

- Coverage badges for README
- Coverage trend reports
- Pull request coverage analysis
- Commit history tracking

Coveralls
~~~~~~~~~

Similar to Codecov:

1. Sign up at coveralls.io
2. Add GitHub repository
3. Upload reports

Additional features:

- Coverage comparison between commits
- Detailed file-by-file reports
- Build and test coverage reports

Coverage Best Practices
-----------------------

1. **Automate Reporting** - Generate and upload automatically
2. **Track Trends** - Monitor coverage over time
3. **Set Goals** - Define acceptable minimums
4. **Review Uncovered** - Understand why code isn't covered
5. **Balance Coverage** - Don't obsess over 100%
6. **Test Behavior** - Focus on behavior, not line coverage
7. **Exclude Generated** - Don't count auto-generated code
8. **Include Tests** - Include test code in coverage metrics
9. **Review Reports** - Regularly review coverage dashboards
10. **Improve Iteratively** - Gradually increase coverage

Troubleshooting Coverage
------------------------

Issue: Coverage Report Missing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``bazel-out/_coverage/_coverage_report.dat`` doesn't exist

**Solutions**:

.. code-block:: bash

    # Ensure test targets exist
    bazel test //:calculator_test

    # Check instrumentation filter
    grep instrumentation_filter BUILD.bazel

    # Generate with explicit options
    bazel coverage --combined_report=lcov --test_output=all //:calculator_test

Issue: 0% Coverage Reported
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Coverage shows 0% even with passing tests

**Solutions**:

.. code-block:: bash

    # Check compilation flags
    bazel coverage --cxxopt='-fprofile-instr-generate' \
                   --cxxopt='-fcoverage-mapping' //:calculator_test

    # Verify instrumentation filter includes targets
    bazel coverage --instrumentation_filter="//..." //:calculator_test

    # Check toolchain supports coverage
    bazel coverage --show_timestamps //:calculator_test

Issue: Coverage Report Too Large
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Report file is too large (> 100MB)

**Solutions**:

.. code-block:: bash

    # Exclude unnecessary files
    bazel coverage --instrumentation_filter="//src/..." //:calculator_test

    # Compress report
    gzip bazel-out/_coverage/_coverage_report.dat

    # Delete old reports
    bazel clean --expunge_async
