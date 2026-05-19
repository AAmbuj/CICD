Testing
=======

Testing Framework
-----------------

The project uses **Google Test (gtest)**, the C++ testing framework by Google.

Benefits of Google Test:

- Simple, intuitive assertion macros
- Automatic test discovery
- Detailed failure messages
- Test fixtures for setup/teardown
- Parametrized tests
- Death tests (for testing crashes)

Test Structure
--------------

Basic Test Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    #include <gtest/gtest.h>
    #include "calculator.h"

    TEST(CalculatorTest, AddWorks) {
        Calculator calc;
        calc.SetOperands(2, 3);
        EXPECT_EQ(calc.Add(), 5.0);
    }

Test Naming Convention
~~~~~~~~~~~~~~~~~~~~~~

- First parameter: Test suite name (e.g., ``CalculatorTest``)
- Second parameter: Test case name (e.g., ``AddWorks``)
- Recommend: ``<Class><Operation><Expected>`` naming

Test Categories
---------------

Unit Tests
~~~~~~~~~~

Tests for individual functions/methods:

.. code-block:: bash

    bazel test //:calculator_test

Integration Tests
~~~~~~~~~~~~~~~~~~

Tests for multiple components working together:

.. code-block:: bash

    # If integration tests exist:
    bazel test //integration:...

Running Tests
-------------

Run All Tests
~~~~~~~~~~~~~

Execute all tests in the project:

.. code-block:: bash

    bazel test //...

Run Specific Test Suite
~~~~~~~~~~~~~~~~~~~~~~~

Run a single test suite:

.. code-block:: bash

    bazel test //:calculator_test

Run with Verbose Output
~~~~~~~~~~~~~~~~~~~~~~~

See detailed test output:

.. code-block:: bash

    bazel test --test_output=all //:calculator_test

Different output options:

.. code-block:: bash

    bazel test --test_output=summary //:calculator_test    # Summary only
    bazel test --test_output=errors //:calculator_test     # Errors only
    bazel test --test_output=all //:calculator_test        # Full output

Filter Tests
~~~~~~~~~~~~

Run specific tests by name:

.. code-block:: bash

    bazel test //:calculator_test --test_filter="*Add*"

Run tests with specific verbosity:

.. code-block:: bash

    # Only run failed tests
    bazel test --test_size_filters=small //:calculator_test

Test Configuration
------------------

Bazel Configuration
~~~~~~~~~~~~~~~~~~~

Test configuration in BUILD.bazel:

.. code-block:: bazel

    cc_test(
        name = "calculator_test",
        srcs = ["tests/unit/calculator_service_test.cc"],
        deps = [
            ":calculator",
            "@google_test//:gtest_main",
        ],
        timeout = "short",  # timeout: short, moderate, long
    )

Test Timeouts
~~~~~~~~~~~~~

Set test timeout:

.. code-block:: bash

    bazel test --test_timeout=300 //:calculator_test

Timeout values (in seconds):

- ``short``: 60 seconds
- ``moderate``: 300 seconds (default)
- ``long``: 900 seconds
- Custom: any number of seconds

Test Execution Modes
~~~~~~~~~~~~~~~~~~~~

Sandbox isolation:

.. code-block:: bash

    bazel test --sandbox //:calculator_test
    bazel test --nosaandbox //:calculator_test  # Disable sandboxing

Run tests in parallel:

.. code-block:: bash

    bazel test --test_jobs=4 //:calculator_test

Test Assertions
---------------

Common Assertions
~~~~~~~~~~~~~~~~~

Equality checks:

.. code-block:: cpp

    ASSERT_EQ(expected, actual);    // Fatal failure
    EXPECT_EQ(expected, actual);    // Non-fatal failure

Comparison checks:

.. code-block:: cpp

    EXPECT_LT(a, b);    // Less than
    EXPECT_LE(a, b);    // Less than or equal
    EXPECT_GT(a, b);    // Greater than
    EXPECT_GE(a, b);    // Greater than or equal

Floating Point Comparisons
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For floating point values, use:

.. code-block:: cpp

    EXPECT_DOUBLE_EQ(expected, actual);      // Exact equality
    EXPECT_NEAR(expected, actual, 0.001);    // Within tolerance

Boolean checks:

.. code-block:: cpp

    EXPECT_TRUE(condition);
    EXPECT_FALSE(condition);

String checks:

.. code-block:: cpp

    EXPECT_STREQ("hello", str);     // Exact match
    EXPECT_STRCASEEQ("HELLO", str); // Case-insensitive

Test Fixtures
-------------

Setup and Teardown
~~~~~~~~~~~~~~~~~~

Use test fixtures for common setup:

.. code-block:: cpp

    class CalculatorTest : public ::testing::Test {
    protected:
        void SetUp() override {
            // Run before each test
            calc.SetOperands(10, 5);
        }

        void TearDown() override {
            // Run after each test
        }

        Calculator calc;
    };

    TEST_F(CalculatorTest, AddCorrect) {
        EXPECT_EQ(15.0, calc.Add());
    }

Parametrized Tests
------------------

Test Multiple Input Combinations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    using CalculatorParamTest = ::testing::TestWithParam<
        std::tuple<double, double, double>
    >;

    TEST_P(CalculatorParamTest, AddParametrized) {
        auto [a, b, expected] = GetParam();
        calc.SetOperands(a, b);
        EXPECT_DOUBLE_EQ(expected, calc.Add());
    }

    INSTANTIATE_TEST_SUITE_P(
        AddTests,
        CalculatorParamTest,
        ::testing::Values(
            std::make_tuple(1.0, 2.0, 3.0),
            std::make_tuple(0.0, 0.0, 0.0),
            std::make_tuple(-1.0, 1.0, 0.0)
        )
    );

Death Tests
-----------

Test for Expected Crashes
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    TEST(CalculatorTest, DivideByZeroFails) {
        ASSERT_DEATH({
            Calculator calc;
            calc.SetOperands(10, 0);
            calc.Divide();  // Should crash
        }, ".*Division by zero.*");
    }

Caution: Death tests are slower, use sparingly.

Code Coverage
-------------

Generate Coverage Report
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    bazel coverage //:calculator_test

The coverage report is written to:

.. code-block:: bash

    bazel-out/_coverage/_coverage_report.dat

Combined coverage for multiple tests:

.. code-block:: bash

    bazel coverage --combined_report=lcov //:calculator_test

Analyze Coverage
~~~~~~~~~~~~~~~~

Convert LCOV to HTML:

.. code-block:: bash

    bazel coverage //:calculator_test
    genhtml bazel-out/_coverage/_coverage_report.dat -o coverage_html
    open coverage_html/index.html

View coverage metrics:

.. code-block:: bash

    lcov --summary bazel-out/_coverage/_coverage_report.dat

Coverage Configuration
~~~~~~~~~~~~~~~~~~~~~~

Configure in .bazelrc or BUILD.bazel:

.. code-block:: bazel

    cc_test(
        name = "calculator_test",
        srcs = ["tests/unit/calculator_service_test.cc"],
        deps = [":calculator", "@google_test//:gtest_main"],
        instrumentation_filter = "//...",
    )

Test Debugging
--------------

Run Single Test with GDB
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    gdb ./bazel-bin/calculator_test

Run with Additional Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    bazel test --test_arg=--gtest_repeat=10 //:calculator_test

Repeat test 10 times for intermittent failures:

.. code-block:: bash

    bazel test --test_arg=--gtest_repeat=100 --test_arg=--gtest_shuffle \
        //:calculator_test

Keep test binaries for inspection:

.. code-block:: bash

    bazel test --cache_test_results=no //:calculator_test

Continuous Integration Testing
-------------------------------

GitHub Actions Workflow
~~~~~~~~~~~~~~~~~~~~~~~~

Tests run automatically on push and pull requests:

.. code-block:: bash

    # In .github/workflows/build_test.yml
    bazel test --test_output=errors //...
    bazel coverage --combined_report=lcov //:calculator_test

View test results in GitHub:

1. Go to your PR or commit
2. Click "Checks" tab
3. View "Build and Test" workflow results

Test Coverage Gates
~~~~~~~~~~~~~~~~~~~

Set minimum coverage requirements:

.. code-block:: bash

    bazel coverage --combined_report=lcov //:calculator_test
    lcov --summary bazel-out/_coverage/_coverage_report.dat | \
        grep -oP '(?<=lines[^:]*:\s)\d+\.\d+(?=%)'

Best Practices
--------------

1. **Write tests early**: Test-driven development (TDD)
2. **Keep tests simple**: Each test should verify one behavior
3. **Use descriptive names**: Test names should explain what's tested
4. **Avoid test interdependence**: Tests should run independently
5. **Test edge cases**: Empty inputs, negative numbers, zero, etc.
6. **Use assertions wisely**: ASSERT for fatal, EXPECT for non-fatal
7. **Mock external dependencies**: Don't test external code
8. **Maintain high coverage**: Aim for 80%+ code coverage
9. **Run tests frequently**: Before commits and in CI/CD
10. **Document test purposes**: Add comments explaining why tests exist

Example Test File Structure
----------------------------

.. code-block:: cpp

    #include <gtest/gtest.h>
    #include "calculator.h"

    // Test Suite Fixture
    class CalculatorTest : public ::testing::Test {
    protected:
        Calculator calc;
    };

    // Test: Addition
    TEST_F(CalculatorTest, AddPositiveNumbers) {
        calc.SetOperands(5, 3);
        EXPECT_DOUBLE_EQ(8.0, calc.Add());
    }

    // Test: Subtraction
    TEST_F(CalculatorTest, SubtractLargerFromSmaller) {
        calc.SetOperands(3, 5);
        EXPECT_DOUBLE_EQ(-2.0, calc.Subtract());
    }

    // Test: Multiplication
    TEST_F(CalculatorTest, MultiplyByZero) {
        calc.SetOperands(5, 0);
        EXPECT_DOUBLE_EQ(0.0, calc.Multiply());
    }

    // Test: Division
    TEST_F(CalculatorTest, DividePositiveNumbers) {
        calc.SetOperands(10, 2);
        EXPECT_DOUBLE_EQ(5.0, calc.Divide());
    }
