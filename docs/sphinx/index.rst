CICD Documentation
==================

This site documents the Bazel-based C++ example project, its CI/CD workflow,
and the quality tooling used to keep the repository easy to maintain and extend.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Started:

   introduction
   quick_start

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Project Documentation:

   architecture
   building
   testing

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Quality Assurance:

   quality
   code_coverage
   dashboard

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Development:

   development
   contributing

Overview
========

The repository is organized around a small calculator application so contributors
can understand the build, test, analysis, and deployment flow without extra noise.

The main pieces are:

* Public interfaces in ``include/calculator``
* Core orchestration in ``src/core``
* Arithmetic operation modules in ``src/operations``
* CLI entry points in ``app``
* Tests in ``tests/unit``
* Docs and quality automation under ``docs`` and ``quality``

Core Workflows
==============

Build, test, and quality checks all run through Bazel:

.. code-block:: bash

   bazel build //...
   bazel test //...
   bazel coverage //:calculator_test
   bazel run //quality/static_analysis:codeql_lint -- --target=//...

Documentation Map
=================

Start here if you are new to the repository:

* :doc:`introduction` for the project goal and key components
* :doc:`quick_start` for the fastest local setup path
* :doc:`architecture` for the module boundaries and extension model
* :doc:`building` for Bazel targets and build patterns
* :doc:`testing` for test execution and verification
* :doc:`quality` for static analysis and quality checks
* :doc:`development` for day-to-day contributor workflow
* :doc:`contributing` for contribution expectations
* :doc:`dashboard` for published metrics and reports

Key Features
============

* **Bazel Build System**: Efficient, scalable build for C++ projects
* **GitHub Actions Pages Deployment**: One workflow publishes docs and dashboard
* **Static Analysis**: Clang-Tidy and CodeQL checks for C++ quality gates
* **Code Coverage**: Bazel-driven LCOV report generation
* **Layered Project Structure**: Clear separation between API, core logic, and CLI
* **Contributor-Focused Docs**: Build, test, quality, and architecture guidance in one place

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
