==================
Contribution Guide
==================

We welcome contributions of all kinds! This guide will help you get started with contributing to Litestar AsyncAPI.

Setting Up Your Development Environment
=======================================

We use ``uv`` for dependency, virtual environment, and tool execution management.

1. **Clone the repository**:

   .. code-block:: bash

       git clone https://github.com/cofin/litestar-asyncapi.git
       cd litestar-asyncapi

2. **Install dependencies**:

   .. code-block:: bash

       make install

3. **Install git hooks (powered by prek)**:

   .. code-block:: bash

       uvx prek install

Development Workflow
====================

1. **Create a branch**:

   .. code-block:: bash

       git checkout -b your-feature-branch

2. **Implement changes**: Follow PEP 585/604 modern typing conventions and enforce docstrings (no inline comments).
3. **Run quality gates**:

   .. code-block:: bash

       make lint          # Runs prek hooks, mypy, pyright, slotscheck, zizmor
       make test          # Run test suite
       make docs          # Build documentation
       make docs-audit    # Verify documentation structural integrity

4. **Run the complete validation suite**:

   .. code-block:: bash

       make check-all     # Aggregate check: lint, test-all, coverage

5. **Commit your changes**: Use Conventional Commits formatting:

   .. code-block:: bash

       git commit -m "feat: your concise summary"

6. **Submit a Pull Request**: Push your branch to GitHub and open a PR against ``main``.

Quality Gates
=============

Every PR must pass our CI matrix before merge:

- **prek / ruff**: Formatting and linting according to Litestar preview rules.
- **mypy & pyright**: Strict type verification scoped to ``src/litestar_asyncapi``.
- **slotscheck**: Validation of ``__slots__`` on all library classes.
- **zizmor**: GitHub Actions workflow security static analysis.
- **pytest**: 100% passing tests across supported Python versions.
- **docs-audit**: Zero structural documentation errors or orphaned pages.
