Quick Start Guide
=================

Prerequisites
-------------

- **Operating System**: Linux (Ubuntu 20.04 or later recommended)
- **Bazel**: Version 7.x or later
- **C++ Compiler**: GCC 9+ or Clang 10+
- **Git**: For version control

Install Bazel
~~~~~~~~~~~~~

Follow the `official Bazel installation guide <https://bazel.build/install>`_ for your operating system.

On Ubuntu:

.. code-block:: bash

    sudo apt-get install bazel

Or using Bazelisk (recommended):

.. code-block:: bash

    curl -LO https://github.com/bazelbuild/bazelisk/releases/download/latest/bazelisk-linux-amd64
    chmod +x bazelisk-linux-amd64
    sudo mv bazelisk-linux-amd64 /usr/local/bin/bazel

Verify installation:

.. code-block:: bash

    bazel --version

Clone and Setup
---------------

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/eclipse-score/cicd.git
    cd CICD

Building the Project
--------------------

Build all targets:

.. code-block:: bash

    bazel build //...

Build the calculator application:

.. code-block:: bash

    bazel build //:calculator

Build the test executable:

.. code-block:: bash

    bazel build //:calculator_test

View build output:

.. code-block:: bash

    # After building, find binaries in:
    ls -la bazel-bin/

Running Tests
-------------

Run all tests:

.. code-block:: bash

    bazel test //...

Run a specific test:

.. code-block:: bash

    bazel test //:calculator_test

Run with verbose output:

.. code-block:: bash

    bazel test --test_output=all //...

Running the Application
------------------------

Run the calculator application:

.. code-block:: bash

    bazel run //:calculator

Expected output:

.. code-block:: text

    Calculator Example
    5 + 3 = 8
    5 - 3 = 2
    5 * 3 = 15
    5 / 3 = 1.66667

Building and Viewing Documentation
-----------------------------------

Build the documentation:

.. code-block:: bash

    bazel build //docs:build_docs

View in your browser:

.. code-block:: bash

    open bazel-bin/docs/_build/index.html

Or serve locally during development:

.. code-block:: bash

    bazel run //docs:serve_docs

Then visit **http://localhost:8000** in your browser.

Running Quality Tools
---------------------

Static Analysis with Clang-Tidy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run Clang-Tidy on all targets:

.. code-block:: bash

    bazel test --config=clang-tidy //...

Run on a specific target:

.. code-block:: bash

    bazel test --config=clang-tidy //:calculator_test

Code Coverage
~~~~~~~~~~~~~

Generate code coverage report:

.. code-block:: bash

    bazel coverage //:calculator_test

The coverage report is generated at:

.. code-block:: text

    bazel-out/_coverage/_coverage_report.dat

View the HTML coverage report (if available):

.. code-block:: bash

    # Coverage files are located in bazel-out/
    find bazel-out -name "*.html" -path "*/coverage*"

CodeQL Security Scanning
~~~~~~~~~~~~~~~~~~~~~~~~

Run CodeQL analysis:

.. code-block:: bash

    bazel run //quality/static_analysis:codeql_lint -- --target=//...

Cleaning Up
-----------

Clean Bazel artifacts:

.. code-block:: bash

    # Remove all build artifacts
    bazel clean

    # Deep clean (removes external dependencies cache)
    bazel clean --expunge

Common Issues
-------------

**Issue**: Bazel not found
  - **Solution**: Ensure Bazel is installed and in your PATH: ``which bazel``

**Issue**: Build fails with C++ compiler errors
  - **Solution**: Ensure C++ compiler is installed: ``sudo apt-get install build-essential``

**Issue**: Permission denied when running scripts
  - **Solution**: Add execute permission: ``chmod +x scripts/run-quality.sh``

**Issue**: Tests timeout
  - **Solution**: Increase timeout: ``bazel test --test_timeout=300 //...``

Next Steps
----------

- Read :doc:`building` for detailed build configuration options
- See :doc:`testing` for comprehensive testing information
- Review :doc:`quality` for code quality tool setup and usage
- Check :doc:`architecture` for project architecture details
