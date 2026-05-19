Building the Project
====================

Build System Overview
---------------------

The project uses Bazel, a modern build system that provides:

- **Fast incremental builds** through dependency tracking
- **Reproducible builds** with exact tool versions
- **Parallel execution** of independent build steps
- **Sandboxed test environment** for isolation
- **Remote execution** capability for distributed builds

Bazel Configuration Files
-------------------------

BUILD.bazel
~~~~~~~~~~~

Defines build targets:

.. code-block:: bazel

    # Library target
    cc_library(
        name = "calculator",
        srcs = ["src/core/calculator_service.cc"],
        hdrs = ["calculator.h"],
    )

    # Executable target
    cc_binary(
        name = "calculator",
        srcs = ["app/cli_main.cc"],
        deps = [":calculator"],
    )

MODULE.bazel
~~~~~~~~~~~~

Declares module metadata and dependencies:

.. code-block:: bazel

    bazel_dep(name = "google_test", version = "1.14.0")

.bazelrc
~~~~~~~~

Build configuration and default flags:

.. code-block:: bash

    # Compiler settings
    build --cxxopt='-std=c++17'
    build --cxxopt='-Wall'
    build --cxxopt='-Wextra'

Building Targets
----------------

Build All Targets
~~~~~~~~~~~~~~~~~~

Build everything in the repository:

.. code-block:: bash

    bazel build //...

This builds all libraries, binaries, and tests.

Build Specific Target
~~~~~~~~~~~~~~~~~~~~~

Build a single target:

.. code-block:: bash

    # Build calculator library
    bazel build //:calculator_lib

    # Build main executable
    bazel build //:calculator

    # Build test executable
    bazel build //:calculator_test

Build with Different Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build with optimization:

.. code-block:: bash

    bazel build -c opt //...

Build with debugging symbols:

.. code-block:: bash

    bazel build -c dbg //...

Build for specific CPU architecture:

.. code-block:: bash

    bazel build --cpu=x86_64 //...

Compiler Options
----------------

C++ Standard
~~~~~~~~~~~~

The project is configured to use C++17:

.. code-block:: bash

    build --cxxopt='-std=c++17'

Warning Flags
~~~~~~~~~~~~~

Enable strict warnings:

.. code-block:: bash

    build --cxxopt='-Wall'      # Enable all warnings
    build --cxxopt='-Wextra'    # Enable extra warnings
    build --cxxopt='-Wpedantic' # Strict ISO compliance

Optimization Levels
~~~~~~~~~~~~~~~~~~~

**Default (fastbuild)**:

- Fast compilation
- Minimal optimization
- Best for development

.. code-block:: bash

    bazel build //...  # Uses fastbuild

**Optimized (-c opt)**:

- Slower compilation
- Maximum optimization
- Smaller binary size
- Best for production

.. code-block:: bash

    bazel build -c opt //...

**Debug (-c dbg)**:

- Slower compilation
- Debugging symbols included
- Best for debugging

.. code-block:: bash

    bazel build -c dbg //...

Build Flags
-----------

Common Build Flags
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Verbose output
    bazel build -s //...

    # Show all build commands
    bazel build --show_timestamps //...

    # Use specific number of CPUs
    bazel build --jobs=4 //...

    # Network isolation
    bazel build --noenable_bzlmod //...

Static vs Shared Libraries
---------------------------

The project builds static libraries by default:

.. code-block:: bazel

    cc_library(
        name = "calculator",
        srcs = ["src/core/calculator_service.cc"],
        hdrs = ["calculator.h"],
        linkstatic = True,  # Force static linking
    )

To use shared libraries:

.. code-block:: bazel

    cc_library(
        name = "calculator",
        srcs = ["src/core/calculator_service.cc"],
        hdrs = ["calculator.h"],
        linkstatic = False,  # Allow shared libraries
    )

Build Artifacts
---------------

Output Locations
~~~~~~~~~~~~~~~~

After building, artifacts are found at:

.. code-block:: bash

    # Compiled binaries
    bazel-bin/
    ├── calculator              # Main executable
    ├── libcalculator.a         # Static library
    └── ...

    # Test executables
    bazel-testlogs/
    ├── calculator_test/        # Test results
    └── ...

    # External dependencies
    bazel-out/
    └── _external/              # Downloaded dependencies

Accessing Build Output
~~~~~~~~~~~~~~~~~~~~~~

Get the path to a built target:

.. code-block:: bash

    bazel run --script=filename //:calculator 2>/dev/null

Or manually:

.. code-block:: bash

    ls -la bazel-bin/
    ./bazel-bin/calculator

Incremental Builds
------------------

Bazel tracks dependencies and only rebuilds affected targets:

.. code-block:: bash

    # First build (full)
    bazel build //...      # Builds all

    # Edit src/core/calculator_service.cc
    bazel build //...      # Rebuilds calculator, calculator_test
                            # But NOT other targets if any

    # Edit only header comment (no code change)
    bazel build //...      # Skips building

This makes iterative development very fast.

Cleaning Build Artifacts
-------------------------

Clean Specific Target
~~~~~~~~~~~~~~~~~~~~~

Remove build output for a target:

.. code-block:: bash

    bazel clean //:calculator

Clean All
~~~~~~~~~

Remove all build artifacts:

.. code-block:: bash

    bazel clean

Deep Clean
~~~~~~~~~~

Remove all artifacts AND external dependencies:

.. code-block:: bash

    bazel clean --expunge

.. warning::

    Deep clean requires re-downloading all external dependencies.
    Only use when necessary.

Cross-Compilation
------------------

Compile for Different Target Platforms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For ARM (e.g., Raspberry Pi):

.. code-block:: bash

    bazel build --cpu=armv7 //...

For ARM64:

.. code-block:: bash

    bazel build --cpu=arm64 //...

For x86:

.. code-block:: bash

    bazel build --cpu=x86 //...

Requires platform-specific toolchain configuration.

Troubleshooting Build Issues
-----------------------------

Issue: "C++ compiler not found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Install build tools

.. code-block:: bash

    # Ubuntu/Debian
    sudo apt-get install build-essential
    sudo apt-get install clang

Issue: "Cannot find dependency"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Check MODULE.bazel and lock file

.. code-block:: bash

    # Update dependencies
    bazel mod tidy
    bazel sync

    # Clean and rebuild
    bazel clean --expunge
    bazel build //...

Issue: "Out of memory during build"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Limit parallel jobs

.. code-block:: bash

    bazel build --jobs=2 //...

    # Or add to .bazelrc
    build --jobs=2

Issue: "Build takes too long"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution**: Check what's being built

.. code-block:: bash

    # Analyze build graph
    bazel query "deps(//:calculator)" | wc -l

    # Build with verbose output
    bazel build -s //... 2>&1 | tail -100

Build Performance Tips
----------------------

1. **Use incremental builds**: Only changed code gets rebuilt
2. **Leverage caching**: Bazel caches intermediate results
3. **Parallelize builds**: Use ``--jobs`` flag
4. **Profile builds**: Use ``bazel build --profile=/tmp/profile.json``
5. **Minimize dependencies**: Only include necessary deps
6. **Use appropriate optimization levels**: Don't over-optimize

Continuous Integration Builds
------------------------------

GitHub Actions Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The CI pipeline uses optimized build settings:

.. code-block:: yaml

    - name: Build
      run: bazel build -c opt //...

    - name: Test
      run: bazel test --test_output=errors //...

    - name: Coverage
      run: bazel coverage --combined_report=lcov //:calculator_test

See `.github/workflows/ <https://github.com/eclipse-score/cicd/tree/main/.github/workflows>`_ for full configurations.
