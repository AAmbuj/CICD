Introduction
=============

Project Overview
----------------

The CICD Project is a demonstration of modern C++ development practices using:

- **Bazel**: A fast, scalable build system with strong dependency management
- **GitHub Actions**: Cloud-based CI/CD automation
- **Quality Tools**: Integrated static analysis, code coverage, and security scanning
- **C++**: A simple calculator application as the example project

Purpose
-------

This project serves as a reference implementation for:

1. Setting up Bazel-based C++ projects
2. Configuring GitHub Actions workflows for CI/CD
3. Integrating quality assurance tools into the build pipeline
4. Writing testable, maintainable C++ code
5. Automating code reviews and security checks

Project Structure
-----------------

.. code-block:: text

    CICD/
    ├── src/core/calculator_service.cc          # Calculator implementation
    ├── calculator.h           # Calculator header
    ├── tests/unit/calculator_service_test.cc     # Unit tests
    ├── app/cli_main.cc                # Example application
    ├── BUILD.bazel            # Bazel build configuration
    ├── MODULE.bazel           # Bazel module definition
    ├── .bazelrc               # Bazel configuration
    ├── .github/
    │   └── workflows/         # GitHub Actions workflows
    ├── quality/
    │   ├── coverage.bazelrc   # Coverage configuration
    │   ├── dashboard/         # Coverage dashboard generation
    │   └── static_analysis/   # Clang-Tidy and CodeQL setup
    ├── scripts/
    │   └── run-quality.sh     # Quality tools script
    ├── tools/
    │   └── lint/              # Linting tools
    └── docs/
        └── sphinx/            # Sphinx documentation (this directory)

Technology Stack
----------------

**Build & Testing:**
- Bazel 7.x - Build system
- GCC/Clang - C++ compilers
- Google Test (gtest) - Unit testing framework

**Code Quality:**
- Clang-Tidy - Static analysis and code style checking
- LCOV - Code coverage measurement
- CodeQL - Security vulnerability scanning

**CI/CD:**
- GitHub Actions - Continuous integration and deployment
- GitHub Workflows - Automated testing and deployment

**Documentation:**
- Sphinx - Documentation generation
- reStructuredText & Markdown - Documentation formats

Key Concepts
------------

Bazel
~~~~~

Bazel is a build system that emphasizes:

- **Reproducibility**: Same inputs always produce the same outputs
- **Scalability**: Works with projects from small to very large
- **Fast**: Incremental builds and parallel execution
- **Sandboxing**: Isolated test environments
- **Remote Execution**: Distribute builds to remote machines

GitHub Actions
~~~~~~~~~~~~~~

GitHub Actions provides:

- **Event-Driven**: Workflows trigger on code pushes, pull requests, etc.
- **No Setup**: Runs on GitHub-hosted runners, no server configuration
- **Flexible**: Can run any task: build, test, deploy, etc.
- **Transparent**: Workflow files are version-controlled in the repository

Quality Tools
~~~~~~~~~~~~~

The project integrates several quality tools:

- **Clang-Tidy**: Lints C++ code for style, performance, and safety issues
- **LCOV**: Measures code coverage to identify untested code
- **CodeQL**: Analyzes code for security vulnerabilities and bugs

Getting Started
---------------

To quickly get started with this project:

1. **Clone the repository**: ``git clone <repo-url>``
2. **Install Bazel**: Follow the `Bazel installation guide <https://bazel.build/install>`_
3. **Build the project**: ``bazel build //...``
4. **Run tests**: ``bazel test //...``
5. **Run the application**: ``bazel run //:calculator``

See :doc:`quick_start` for detailed instructions.

Learning Resources
-------------------

- `Bazel Documentation <https://bazel.build/docs>`_
- `GitHub Actions Documentation <https://docs.github.com/en/actions>`_
- `Clang-Tidy Documentation <https://clang.llvm.org/extra/clang-tidy/>`_
- `LCOV Documentation <http://ltp.sourceforge.net/coverage/lcov.php>`_
