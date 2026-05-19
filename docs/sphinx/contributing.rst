Contributing
=============

How to Contribute
-----------------

We welcome contributions from the community! This guide will help you understand how to contribute effectively.

Getting Started
---------------

1. **Fork the Repository**

   Go to the `GitHub repository <https://github.com/eclipse-score/cicd>`_ and click "Fork"

2. **Clone Your Fork**

   .. code-block:: bash

       git clone https://github.com/YOUR-USERNAME/cicd.git
       cd CICD

3. **Create a Feature Branch**

   .. code-block:: bash

       git checkout -b feature/your-feature-name

4. **Set Up Development Environment**

   .. code-block:: bash

       # Install dependencies
       sudo apt-get install build-essential clang-format clang-tools

       # Verify Bazel installation
       bazel --version

Contribution Types
------------------

Bug Fixes
~~~~~~~~~

To fix a bug:

1. **Create an Issue**: Describe the bug with steps to reproduce
2. **Create a Branch**: ``git checkout -b fix/issue-description``
3. **Fix the Bug**: Make minimal, focused changes
4. **Add Tests**: Include regression tests
5. **Submit PR**: Link the issue in the PR description

Features
~~~~~~~~

To add a feature:

1. **Discuss First**: Create an issue proposing the feature
2. **Get Feedback**: Wait for maintainers to review
3. **Create Branch**: ``git checkout -b feature/feature-name``
4. **Implement**: Follow code standards
5. **Document**: Update relevant documentation
6. **Test**: Add comprehensive tests
7. **Submit PR**: Reference the feature issue

Documentation
~~~~~~~~~~~~~

To improve documentation:

1. **Fork and Clone**: Set up your development environment
2. **Edit Files**: Update ``.rst`` or ``.md`` files in ``docs/sphinx/``
3. **Preview**: Build documentation locally:

   .. code-block:: bash

       cd docs/sphinx
       sphinx-build -b html . _build

4. **Submit PR**: Include preview of changes

Code Style
----------

C++ Style Guide
~~~~~~~~~~~~~~~

Follow Google C++ Style Guide with exceptions:

- **Indentation**: 4 spaces
- **Line Length**: 100 characters
- **Braces**: Allman style for class/function definitions
- **Comments**: Clear, concise, helpful

Example:

.. code-block:: cpp

    /// Brief description of the function.
    ///
    /// Longer description explaining behavior, edge cases,
    /// and any important implementation details.
    ///
    /// \param input Description of input parameter
    /// \return Description of return value
    /// \throws std::invalid_argument if input is invalid
    int ProcessData(const std::string& input);

Formatting
~~~~~~~~~~

Automatic formatting with clang-format:

.. code-block:: bash

    # Format your changes
    clang-format -i src/core/calculator_service.cc

    # Check formatting without modifying
    clang-format --dry-run src/core/calculator_service.cc

All code must pass clang-format before merging.

Code Standards
~~~~~~~~~~~~~~

- **No warnings**: Code must compile without warnings
- **No magic numbers**: Use named constants
- **Const correctness**: Mark parameters const when appropriate
- **Memory safety**: Use smart pointers, avoid raw ``new/delete``
- **Error handling**: Use exceptions for error conditions
- **Testability**: Design for unit testing

Testing Requirements
--------------------

All Changes Require Tests
~~~~~~~~~~~~~~~~~~~~~~~~~

- **New features**: Add new unit tests
- **Bug fixes**: Add regression test demonstrating the bug
- **Modifications**: Update existing tests

Test Coverage
~~~~~~~~~~~~~

Maintain or improve test coverage:

.. code-block:: bash

    # Generate coverage report
    bazel coverage //:calculator_test

    # View results
    genhtml bazel-out/_coverage/_coverage_report.dat -o coverage_html
    open coverage_html/index.html

Aim for **80%+ code coverage**.

Running Tests
~~~~~~~~~~~~~

Before submitting a PR, run all tests:

.. code-block:: bash

    # Run all tests
    bazel test //...

    # Run with verbose output
    bazel test --test_output=all //...

    # Run with specific configuration
    bazel test --config=clang-tidy //...

Static Analysis
~~~~~~~~~~~~~~~

Code must pass static analysis:

.. code-block:: bash

    # Run Clang-Tidy
    bazel test --config=clang-tidy //...

    # Run CodeQL
    bazel run //quality/static_analysis:codeql_lint -- --target=//...

Pull Request Process
--------------------

Before Creating a PR
~~~~~~~~~~~~~~~~~~~~

1. **Update your branch** with latest changes:

   .. code-block:: bash

       git fetch origin
       git rebase origin/main

2. **Run all checks**:

   .. code-block:: bash

       bazel test //...
       bazel test --config=clang-tidy //...
       bazel coverage //:calculator_test

3. **Fix any issues**: Ensure all tests pass and quality checks pass

4. **Clean commit history**: Squash fixup commits:

   .. code-block:: bash

       git rebase -i origin/main

Creating the PR
~~~~~~~~~~~~~~~

1. **Push your branch**:

   .. code-block:: bash

       git push origin feature/your-feature-name

2. **Create PR on GitHub**:

   - Set base branch to ``main``
   - Write descriptive PR title and description
   - Link related issues: ``Fixes #123`` or ``Related to #456``

3. **PR Description Template**:

   .. code-block:: markdown

       ## Description
       Brief description of what this PR does.

       ## Motivation
       Why is this change needed?

       ## Changes
       - Bullet point 1
       - Bullet point 2

       ## Testing
       How was this tested?

       ## Checklist
       - [ ] Tests added/updated
       - [ ] Documentation updated
       - [ ] Code formatted (clang-format)
       - [ ] No compiler warnings
       - [ ] No Clang-Tidy warnings
       - [ ] Coverage maintained or improved

PR Review Process
~~~~~~~~~~~~~~~~~

1. **Automated Checks**: GitHub Actions runs tests
2. **Code Review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: PR approved by maintainers
5. **Merge**: PR merged into main branch

Common Review Feedback
~~~~~~~~~~~~~~~~~~~~~~

- **Style Issues**: Format according to style guide
- **Missing Tests**: Add tests for uncovered code
- **Documentation**: Update docs if behavior changes
- **Performance**: Optimize slow operations
- **Compatibility**: Ensure backward compatibility
- **Security**: Follow security best practices

Commit Guidelines
-----------------

Commit Message Format
~~~~~~~~~~~~~~~~~~~~~

Follow conventional commits:

.. code-block:: text

    type(scope): subject

    body

    footer

- **type**: ``feat``, ``fix``, ``docs``, ``style``, ``refactor``, ``test``, ``chore``
- **scope**: affected area (e.g., calculator, build)
- **subject**: imperative mood, lowercase, < 50 chars
- **body**: explain what and why, wrap at 72 chars
- **footer**: reference issues: ``Fixes #123``

Examples:

.. code-block:: bash

    git commit -m "feat(calculator): add modulo operation

    Add modulo (remainder) operation to calculator.
    Implements the % operator for integer operands.

    Fixes #42"

    git commit -m "fix(tests): correct floating point comparison

    Use EXPECT_NEAR instead of EXPECT_EQ for comparing
    floating point values to account for rounding errors."

Good Commits
~~~~~~~~~~~~

- **Atomic**: Each commit does one thing
- **Testable**: Each commit is independently testable
- **Buildable**: Each commit builds without errors
- **Meaningful**: Commit message explains the why
- **Small**: Easier to review and understand

Avoid:

- **Merge commits**: Use rebase instead
- **Large commits**: Split into smaller commits
- **Vague messages**: ``fix bug`` or ``update code``
- **Formatting fixes**: Separate from logic changes

Documentation Updates
---------------------

Updating Sphinx Docs
~~~~~~~~~~~~~~~~~~~~

Documentation files are in ``docs/sphinx/``:

1. **Edit .rst files**: Restructured Text format
2. **Follow conventions**: See existing files for style
3. **Build locally**: Verify changes render correctly:

   .. code-block:: bash

       cd docs/sphinx
       sphinx-build -b html . _build
       open _build/index.html

4. **Submit with PR**: Include documentation changes with code

Adding New Pages
~~~~~~~~~~~~~~~~

1. **Create .rst file**:

   .. code-block:: bash

       touch docs/sphinx/new_page.rst

2. **Add content** using reStructuredText:

   .. code-block:: rst

       New Page Title
       ==============

       Content here...

3. **Link from index.rst**:

   .. code-block:: rst

       .. toctree::
          :maxdepth: 2

          new_page

4. **Build and test**:

   .. code-block:: bash

       sphinx-build -b html . _build

Reporting Issues
----------------

Bug Reports
~~~~~~~~~~~

Include:

1. **Title**: Clear, descriptive summary
2. **Description**: What's the problem?
3. **Steps to Reproduce**: Exact steps to reproduce
4. **Expected Behavior**: What should happen?
5. **Actual Behavior**: What actually happens?
6. **Environment**:

   - OS (Linux distribution, version)
   - Bazel version (``bazel --version``)
   - C++ compiler (``g++ --version`` or ``clang --version``)
   - Build output (error log)

7. **Additional Context**: Screenshots, logs, etc.

Feature Requests
~~~~~~~~~~~~~~~~

Include:

1. **Title**: Clear feature description
2. **Motivation**: Why is this feature needed?
3. **Proposed Solution**: How should it work?
4. **Alternatives**: Other solutions considered?
5. **Additional Context**: Examples, use cases

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

We are committed to providing a welcoming and inclusive environment.

- **Respect others**: Treat everyone with respect
- **Be inclusive**: Welcome people from all backgrounds
- **Be helpful**: Assist others in the community
- **Report issues**: Flag inappropriate behavior to maintainers
- **Be patient**: Remember everyone is volunteering

Community Standards
~~~~~~~~~~~~~~~~~~~

- Use clear, professional language
- Provide constructive feedback
- Ask questions if you don't understand
- Help newer contributors get started
- Recognize contributions of others

Getting Help
~~~~~~~~~~~~

Need help? Ask in:

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Email**: contact@example.com for private concerns

Additional Resources
--------------------

- `Bazel Documentation <https://bazel.build/docs>`_
- `Google C++ Style Guide <https://google.github.io/styleguide/cppguide.html>`_
- `Sphinx Documentation <https://www.sphinx-doc.org/>`_
- `GitHub Guides <https://guides.github.com/>`_

Thank You
---------

Thank you for contributing to the CICD Project!

Your contributions help make this project better for everyone.
