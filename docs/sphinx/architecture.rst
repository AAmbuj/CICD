Architecture
============

Project Architecture Overview
-----------------------------

The project follows a layered and module-oriented structure that keeps the
public API stable while making implementation easy to extend.

.. code-block:: text

    ┌────────────────────────────────────────────────────────────┐
    │ Application Layer                                          │
    │  app/cli_main.cc                                           │
    └──────────────────────────────┬─────────────────────────────┘
                                   │
    ┌──────────────────────────────▼─────────────────────────────┐
    │ Core Service Layer                                         │
    │  include/calculator/calculator_service.h                   │
    │  src/core/calculator_service.cc                            │
    └──────────────────────────────┬─────────────────────────────┘
                                   │
    ┌──────────────────────────────▼─────────────────────────────┐
    │ Operation Modules                                          │
    │  include/calculator/operations/arithmetic_operations.h     │
    │  src/operations/arithmetic_operations.cc                   │
    │  include/calculator/operations.h (compatibility include)   │
    └────────────────────────────────────────────────────────────┘

Code Layout
-----------

Public Headers
~~~~~~~~~~~~~~

- ``include/calculator/calculator_service.h``: service-level API.
- ``include/calculator/operations/arithmetic_operations.h``: module-level API for arithmetic operations.
- ``include/calculator/operations.h``: backward-compatible include that forwards to the module header.
- ``calculator.h``: backward-compatible alias for older callers.

Implementation
~~~~~~~~~~~~~~

- ``src/core/calculator_service.cc``: orchestrates operation modules.
- ``src/operations/arithmetic_operations.cc``: operation implementation with local validation (for example, divide-by-zero checks).

Tests
~~~~~

- ``tests/unit/calculator_service_test.cc``: behavior tests against public interfaces.

Build Architecture
------------------

The root ``BUILD.bazel`` separates the code into focused targets:

- ``:calculator_operations``: operation module target.
- ``:calculator_core``: service target that depends on operation modules.
- ``:calculator_lib``: stable public library target used by applications/tests.
- ``:calculator``: CLI binary.
- ``:calculator_test``: unit test target.

This split keeps dependencies clear and allows adding new modules without
turning one target into a monolith.

Dependency Flow
---------------

.. code-block:: text

    :calculator (binary)
        -> :calculator_lib
            -> :calculator_core
                -> :calculator_operations

Extension Workflow
------------------

To add a new feature module:

1. Add a public header under ``include/calculator/<module>/``.
2. Add implementation under ``src/<module>/``.
3. Add a dedicated ``cc_library`` target in ``BUILD.bazel``.
4. Wire it into ``:calculator_core`` only if orchestration is required.
5. Add tests under ``tests/unit/``.

Maintenance Rules
-----------------

1. Keep app-level I/O in ``app/`` only.
2. Keep business orchestration in ``src/core/``.
3. Keep algorithm/operation logic in module folders under ``src/operations/`` (or new module names).
4. Preserve compatibility headers when moving public interfaces.
5. Remove stale files and empty placeholder directories during refactors.

Quality and CI/CD
-----------------

Quality checks are integrated through Bazel and GitHub Actions:

- Build: ``bazel build //...``
- Test: ``bazel test //...``
- Coverage: ``bazel coverage //:calculator_test``
- Static analysis: CodeQL and clang-tidy via existing quality targets
