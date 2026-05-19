Development Guide
==================

Setting Up Development Environment
-----------------------------------

Prerequisites
~~~~~~~~~~~~~

- **Operating System**: Linux (Ubuntu 20.04+)
- **Bazel**: 7.x or later
- **C++ Compiler**: GCC 9+ or Clang 10+
- **Python**: 3.11+ (for scripts and tools)
- **Git**: For version control

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

Ubuntu/Debian:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install build-essential
    sudo apt-get install clang clang-format clang-tools
    sudo apt-get install python3-dev python3-pip
    sudo apt-get install git

Install Bazel:

.. code-block:: bash

    curl https://bazel.build/bazel-release.pub | sudo apt-key add -
    echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt focal main" | \
        sudo tee /etc/apt/sources.list.d/bazel-focal.list
    sudo apt-get update && sudo apt-get install bazel

Development Workflow
--------------------

Code-Edit-Test Cycle
~~~~~~~~~~~~~~~~~~~~

1. **Make Changes**: Edit source files

.. code-block:: bash

    vim src/core/calculator_service.cc

2. **Build Incrementally**: Bazel rebuilds only what changed

.. code-block:: bash

    bazel build //:calculator

3. **Run Tests**: Verify your changes

.. code-block:: bash

    bazel test //:calculator_test

4. **Check Quality**: Run static analysis

.. code-block:: bash

    bazel test --config=clang-tidy //:calculator_test

5. **Commit Changes**: Version control

.. code-block:: bash

    git add src/core/calculator_service.cc
    git commit -m "Add feature: ..."

Development Tips
~~~~~~~~~~~~~~~~

- **Use incremental builds**: Only changed code is rebuilt
- **Run tests before committing**: Ensure nothing breaks
- **Check formatting**: Use clang-format before commit
- **Review warnings**: Fix compiler warnings immediately
- **Write tests first**: Test-driven development (TDD)

Directory Layout
----------------

Source Code
~~~~~~~~~~~

Main source files:

.. code-block:: text

    /
    ├── calculator.h         # Calculator interface
    ├── src/core/calculator_service.cc        # Calculator implementation
    └── app/cli_main.cc              # Example application

Tests
~~~~~

Test files:

.. code-block:: text

    /
    └── tests/unit/calculator_service_test.cc   # Unit tests

Build Configuration
~~~~~~~~~~~~~~~~~~~

Bazel files:

.. code-block:: text

    /
    ├── BUILD.bazel          # Build targets
    ├── MODULE.bazel         # Module definition
    ├── .bazelrc             # Build configuration
    └── .bazelversion        # Bazel version lock

Code Style Guide
----------------

Naming Conventions
~~~~~~~~~~~~~~~~~~

**Classes**: PascalCase

.. code-block:: cpp

    class Calculator { };
    class DataProcessor { };

**Functions**: PascalCase

.. code-block:: cpp

    double Add();
    void SetOperands(double lhs, double rhs);

**Variables**: snake_case

.. code-block:: cpp

    double lhs, rhs;
    int iteration_count = 0;

**Constants**: UPPER_SNAKE_CASE

.. code-block:: cpp

    const double PI = 3.14159;
    const int MAX_ITERATIONS = 100;

**Member Variables**: ``m_`` prefix + snake_case

.. code-block:: cpp

    class Calculator {
        double m_lhs;
        double m_rhs;
    };

Code Formatting
~~~~~~~~~~~~~~~

Use clang-format (configured in **.clang-format**):

.. code-block:: bash

    # Format single file
    clang-format -i src/core/calculator_service.cc

    # Format all C++ files
    find . -name "*.cc" -o -name "*.h" | xargs clang-format -i

    # Check without modifying
    clang-format --dry-run src/core/calculator_service.cc

Key style rules:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters maximum
- **Braces**: Google style (opening on same line)
- **Comments**: Spaces before comment marker: ``// Comment``

Include Guards
~~~~~~~~~~~~~~

Use ``#pragma once`` for headers:

.. code-block:: cpp

    #pragma once

    class Calculator {
        // ...
    };

Documentation Style
~~~~~~~~~~~~~~~~~~~

Use Google-style comments:

.. code-block:: cpp

    /// Brief description of function.
    ///
    /// Longer description explaining the function behavior,
    /// parameters, return value, and any side effects.
    ///
    /// \param lhs Left-hand operand
    /// \param rhs Right-hand operand
    /// \return Result of operation
    double Add(double lhs, double rhs);

Headers:

.. code-block:: cpp

    // Copyright notice
    // License information
    // Brief file description

    #pragma once

    #include <required_header>

    // ...

Creating New Files
------------------

Adding a New Source File
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create the file with proper header:

.. code-block:: cpp

    // Copyright (c) 2026 Contributors to the Eclipse Foundation
    // SPDX-License-Identifier: Apache-2.0

    #pragma once

    /// Brief description
    class MyClass {
    public:
        /// Constructor
        MyClass();

        /// Public method
        void DoSomething();

    private:
        // Private members
    };

2. Update BUILD.bazel to include the file:

.. code-block:: bazel

    cc_library(
        name = "my_library",
        srcs = ["my_class.cc"],
        hdrs = ["my_class.h"],
    )

3. Add unit tests:

.. code-block:: cpp

    #include <gtest/gtest.h>
    #include "my_class.h"

    TEST(MyClassTest, ConstructorWorks) {
        MyClass obj;
        // Test assertions
    }

Adding a New Test
~~~~~~~~~~~~~~~~~

1. Create test file:

.. code-block:: bash

    cp tests/unit/calculator_service_test.cc new_test.cc

2. Update test class and function names
3. Update BUILD.bazel:

.. code-block:: bazel

    cc_test(
        name = "new_test",
        srcs = ["new_test.cc"],
        deps = [":calculator", "@google_test//:gtest_main"],
    )

4. Run the test:

.. code-block:: bash

    bazel test //:new_test

Dependency Management
---------------------

External Dependencies
~~~~~~~~~~~~~~~~~~~~~

Declared in **MODULE.bazel**:

.. code-block:: bazel

    bazel_dep(name = "google_test", version = "1.14.0")
    bazel_dep(name = "abseil-cpp", version = "20230125.3")

Add a new dependency:

.. code-block:: bash

    # 1. Update MODULE.bazel
    bazel_dep(name = "nlohmann_json", version = "3.11.2")

    # 2. Update lock file
    bazel mod tidy

    # 3. Update BUILD.bazel to use dependency
    cc_library(
        name = "json_parser",
        srcs = ["parser.cc"],
        deps = ["@nlohmann_json//:json"],
    )

Internal Dependencies
~~~~~~~~~~~~~~~~~~~~~

Targets depending on other targets:

.. code-block:: bazel

    cc_binary(
        name = "calculator",
        srcs = ["app/cli_main.cc"],
        deps = [":calculator_lib"],  # Internal dependency
    )

    cc_library(
        name = "calculator_lib",
        srcs = ["src/core/calculator_service.cc"],
        hdrs = ["calculator.h"],
    )

Debugging
---------

Debug with GDB
~~~~~~~~~~~~~~

Compile with debug symbols:

.. code-block:: bash

    bazel build -c dbg //:calculator

Debug with GDB:

.. code-block:: bash

    gdb ./bazel-bin/calculator

GDB commands:

.. code-block:: bash

    (gdb) run                    # Run program
    (gdb) break main             # Set breakpoint
    (gdb) continue               # Continue execution
    (gdb) step                   # Step into function
    (gdb) next                   # Step over function
    (gdb) print variable_name    # Print variable
    (gdb) backtrace              # Show call stack

Debug with Print Statements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add logging:

.. code-block:: cpp

    #include <iostream>

    std::cout << "Debug: value = " << value << std::endl;

Compile with verbose output:

.. code-block:: bash

    bazel build -s //:calculator

Print Bazel debug info:

.. code-block:: bash

    bazel --debug query "deps(//:calculator)"

Analyzing Build Performance
---------------------------

Profile Build
~~~~~~~~~~~~~~

.. code-block:: bash

    bazel build --profile=/tmp/profile.json //:calculator
    bazel analyze-profile /tmp/profile.json

View results:

.. code-block:: bash

    # Analyze-profile output shows slowest steps
    # Top 20 longest build steps

Analyze Dependency Graph
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # List all dependencies
    bazel query "deps(//:calculator)" | sort

    # Show dependency tree
    bazel query --output=graph "deps(//:calculator)" > graph.in
    dot -Tpng graph.in > graph.png

Optimize Build
~~~~~~~~~~~~~~

1. Reduce dependencies (only include needed)
2. Split large libraries into smaller ones
3. Use incremental builds (Bazel default)
4. Parallelize tests: ``--test_jobs=N``

Version Control
---------------

Git Workflow
~~~~~~~~~~~~

Typical workflow:

.. code-block:: bash

    # Create feature branch
    git checkout -b feature/my-feature

    # Make changes and commit
    git add .
    git commit -m "Add my feature"

    # Push to remote
    git push origin feature/my-feature

    # Create pull request on GitHub
    # (specify base branch as main/master)

Commit Message Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~

Follow conventional commits:

.. code-block:: text

    type(scope): description

    - type: feat, fix, docs, style, refactor, test, chore
    - scope: area affected (calculator, build, etc.)
    - description: clear, concise summary (imperative mood)

Examples:

.. code-block:: bash

    git commit -m "feat(calculator): add division operation"
    git commit -m "fix(tests): correct floating point comparison"
    git commit -m "docs(readme): update build instructions"
    git commit -m "style: format code with clang-format"

Pre-commit Hooks
~~~~~~~~~~~~~~~~

Setup pre-commit checks:

.. code-block:: bash

    pip install pre-commit
    pre-commit install

Runs automatically before commit:

- Code formatting check
- Linting
- Unit tests (optional)

Continuous Development
----------------------

Watch Mode
~~~~~~~~~~

Automatically rebuild on file changes:

.. code-block:: bash

    # Monitor and rebuild on changes
    bazel build --watch //:calculator

Testing During Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run tests frequently:

.. code-block:: bash

    # Every time you change code
    bazel test //:calculator_test

    # After significant changes
    bazel test //...

    # Before committing
    bazel test --test_output=all //...

Documentation
~~~~~~~~~~~~~

Update documentation when changing code:

- Class/function docstrings
- README.md updates
- Architecture documentation
- Comment code that's not obvious

IDE Integration
---------------

VS Code Setup
~~~~~~~~~~~~~

1. Install C++ extension: ``ms-vscode.cpptools``
2. Install Bazel extension: ``BazelBuild.bazel``
3. Configure settings:

.. code-block:: json

    {
        "C_Cpp.default.compileCommands": "${workspaceFolder}/compile_commands.json",
        "bazel.buildifierFixOnFormat": true,
        "bazel.lintOnSave": true
    }

Generate compile_commands:

.. code-block:: bash

    bazel run @hedron_compile_commands//:refresh_all

CLion/IntelliJ IDEA
~~~~~~~~~~~~~~~~~~~

1. Install Bazel plugin
2. Open project with Bazel
3. Configure Bazel settings
4. Build targets from IDE

Development Best Practices
---------------------------

1. **Incremental Development**: Make small, testable changes
2. **TDD**: Write tests before code
3. **Code Review**: Have peers review changes
4. **Continuous Testing**: Run tests frequently
5. **Quality First**: Fix warnings and style issues
6. **Documentation**: Keep docs updated with code
7. **Version Control**: Commit often with clear messages
8. **Performance**: Profile before optimizing
9. **Security**: Follow security best practices
10. **Communication**: Discuss architectural changes early
