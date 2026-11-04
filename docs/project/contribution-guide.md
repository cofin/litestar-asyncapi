# Contribution guide

We welcome contributions of all kinds! This guide will help you get started with contributing to Litestar AsyncAPI.

## Setting up your development environment

We use `uv` for dependency, virtual environment, and tool execution management.

1. **Clone the repository**:

    ```bash
    git clone https://github.com/cofin/litestar-asyncapi.git
    cd litestar-asyncapi
    ```

2. **Install dependencies**:

    ```bash
    make install
    ```

3. **Install git hooks (powered by prek)**:

    ```bash
    uvx prek install
    ```

## Development workflow

1. **Create a branch**:

    ```bash
    git checkout -b your-feature-branch
    ```

2. **Implement changes**: Follow PEP 585/604 modern typing conventions and enforce docstrings (no inline comments).
3. **Run quality gates**:

    ```bash
    make lint          # Runs prek hooks, mypy, pyright, slotscheck, zizmor and PEP 723 checks
    make test          # Run test suite, including every docs example
    make docs          # Build the documentation site and verify its links and redirects
    ```

4. **Run the complete validation suite**:

    ```bash
    make check-all     # Aggregate check: lint, then tests with coverage
    ```

5. **Commit your changes**: Use Conventional Commits formatting:

    ```bash
    git commit -m "feat: your concise summary"
    ```

6. **Submit a Pull Request**: Push your branch to GitHub and open a PR against `main`.

## Quality gates

Every PR must pass our CI matrix before merge:

- **prek / ruff**: Formatting and linting according to Litestar preview rules.
- **mypy & pyright**: Strict type verification scoped to `src/litestar_asyncapi`.
- **slotscheck**: Validation of slotted library classes, with narrow exclusions for adapters inheriting native unslotted Litestar render classes.
- **zizmor**: GitHub Actions workflow security static analysis.
- **pytest**: 100% passing tests across supported Python versions, including every runnable docs example.
- **docs**: A Zensical build with zero warnings, resolving internal links, anchors and legacy redirects, plus an external link check.

## Documentation

The site is built with [Zensical](https://zensical.org/) from Markdown under `docs/`.
Building it needs Python 3.11 or newer; `make docs` creates a separate `.venv-docs`
environment for it, so the development environment can stay on Python 3.10.

```bash
make docs            # Build, write legacy redirects and verify the site
make docs-serve      # Live preview at http://127.0.0.1:8000/litestar-asyncapi/
make docs-linkcheck  # Check external links with lychee, when installed
```

## Packaged frontend and distribution

Node is needed only to build and test the packaged UI, not to install or use the Python package.
Use the version pinned in `.nvmrc`, for example with `nvm use`, then the locked npm dependencies
and native targets:

```bash
nvm use
npm ci
make js-test validate-asyncapi browser-test
make build
make installed-test PYTHON_VERSION=3.12
make browser-test-installed
make docs docs-linkcheck validate-pep723
```

The release workflow publishes the same wheel that passed installed Python and
browser checks. JSON/YAML export and normal package imports do not require Node.
The official document gate and separate Draft07 instance checks have distinct
responsibilities: parser acceptance alone does not validate example payloads.
`make validate-asyncapi` also exports every docs example's document and validates it.
