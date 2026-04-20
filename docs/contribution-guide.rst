==================
Contribution Guide
==================

We welcome contributions of all kinds! This guide will help you get started with contributing to Litestar AsyncAPI.

Setting Up Your Development Environment
=======================================

We use ``uv`` for dependency and environment management.

1.  **Clone the repository**:

    .. code-block:: bash

        git clone https://github.com/litestar-org/litestar-asyncapi.git
        cd litestar-asyncapi

2.  **Install dependencies and set up pre-commit**:

    .. code-block:: bash

        uv sync
        uv run pre-commit install

Development Workflow
====================

1.  **Create a branch**:

    .. code-block:: bash

        git checkout -b your-feature-branch

2.  **Make your changes**: Implement your feature or fix your bug.
3.  **Run quality checks**: Use the provided Makefile targets to ensure your changes meet our standards.

    .. code-block:: bash

        make lint  # Run all linters and formatters
        make test  # Run all tests
        make docs  # Build documentation

4.  **Commit your changes**: We use conventional commits.

    .. code-block:: bash

        git commit -m "feat: your new feature"

5.  **Push your branch**:

    .. code-block:: bash

        git push origin your-feature-branch

6.  **Open a Pull Request**: Submit your PR on GitHub and wait for review.

Quality Gates
=============

We use several tools to maintain code quality:

- **Ruff**: For linting and formatting.
- **Mypy/Pyright**: For type checking.
- **Pytest**: For testing.
- **Slotscheck**: To ensure ``__slots__`` are correctly defined.

All checks must pass before a PR can be merged.

Documentation
=============

Documentation is located in the ``docs/`` directory and is built using Sphinx. We use the Shibuya theme with AsyncAPI-specific styling.

To build the documentation locally:

.. code-block:: bash

    make docs

To serve the documentation with live-reload:

.. code-block:: bash

    uv run sphinx-autobuild docs docs/_build/html

Issue Tracking
==============

We use **bd (beads)** for issue tracking and development workflows. See the ``AGENTS.md`` for more details on how to use ``bd``.
