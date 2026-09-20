SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

# =============================================================================
# Configuration and Environment Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
.EXPORT_ALL_VARIABLES:
MAKEFLAGS += --no-print-directory
PYTHON_VERSION ?= 3.10
UV_SYNC_ARGS ?= --all-extras --dev

# Detect Rodete and configure index URLs for Python tools
ifneq ($(shell grep -s -q "rodete" /etc/os-release && echo "yes"),)
export PIP_INDEX_URL=https://pypi.org/simple
export UV_INDEX_URL=https://pypi.org/simple
endif

# -----------------------------------------------------------------------------
# Display Formatting and Colors
# -----------------------------------------------------------------------------
BLUE := $(shell printf "\033[1;34m")
GREEN := $(shell printf "\033[1;32m")
RED := $(shell printf "\033[1;31m")
YELLOW := $(shell printf "\033[1;33m")
NC := $(shell printf "\033[0m")
INFO := $(shell printf "$(BLUE)ℹ$(NC)")
OK := $(shell printf "$(GREEN)✓$(NC)")
WARN := $(shell printf "$(YELLOW)⚠$(NC)")
ERROR := $(shell printf "$(RED)✖$(NC)")

# =============================================================================
# Help and Documentation
# =============================================================================

.PHONY: help
help:                                               ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# =============================================================================
# Installation and Environment Setup
# =============================================================================

.PHONY: setup-env
setup-env:                                          ## Configure local environment (e.g. Rodete)
	@./tools/scripts/setup-env.sh

.PHONY: install-uv
install-uv:                                         ## Install latest version of uv
	@echo "${INFO} Installing uv... ⚡"
	@curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
	@echo "${OK} UV installed successfully 🎉"

.PHONY: install
install: destroy clean setup-env                    ## Install all locked development dependencies
	@echo "${INFO} Starting fresh installation... ⚡"
	@uv python pin $(PYTHON_VERSION) >/dev/null 2>&1
	@uv venv >/dev/null 2>&1
	@uv sync $(UV_SYNC_ARGS)
	@echo "${OK} Installation complete! 🎉"

.PHONY: destroy
destroy:                                            ## Destroy virtual environment and clean caches
	@echo "${INFO} Destroying virtual environment... 🗑️"
	@uvx prek clean >/dev/null 2>&1 || true
	@rm -rf .venv
	@echo "${OK} Virtual environment destroyed 🗑️"

# =============================================================================
# Dependency Management
# =============================================================================

.PHONY: upgrade
upgrade:                                            ## Upgrade all dependencies to latest stable versions
	@echo "${INFO} Updating all dependencies... 🔄"
	@uv lock --upgrade
	@echo "${OK} Dependencies updated 🔄"
	@uvx prek autoupdate --cooldown-days 7
	@echo "${OK} Updated prek hooks (7-day cooldown) 🔄"
	@uv lock >/dev/null 2>&1

.PHONY: lock
lock:                                               ## Rebuild lockfiles from scratch
	@echo "${INFO} Rebuilding lockfiles... 🔄"
	@uv lock --upgrade >/dev/null 2>&1
	@echo "${OK} Lockfiles updated 🔄"

# =============================================================================
# Build and Release
# =============================================================================

.PHONY: build
build: js-build                                    ## Build the project
	@echo "${INFO} Building package... 📦"
	@uv build
	@uv run python frontend/tests/distribution.py
	@echo "${OK} Package build complete 📦"

.PHONY: release
release:                                           ## Bump version and create release tag (bump=major|minor|patch)
	@if [ -z "$(bump)" ]; then \
		echo "${ERROR} Usage: make release bump=major|minor|patch"; \
		exit 1; \
	fi
	@echo "${INFO} Preparing for release... 📦"
	@make docs
	@make clean
	@make build
	@uv run bump-my-version bump $(bump)
	@uv lock --upgrade-package litestar-asyncapi >/dev/null 2>&1
	@echo "${OK} Release complete 🎉"

.PHONY: pre-release
pre-release:                                       ## Start a pre-release: make pre-release version=0.2.0-alpha.1
	@if [ -z "$(version)" ]; then \
		echo "${ERROR} Usage: make pre-release version=X.Y.Z-alpha.N"; \
		echo ""; \
		echo "Pre-release workflow:"; \
		echo "  1. Start alpha:     make pre-release version=0.2.0-alpha.1"; \
		echo "  2. Next alpha:      make pre-release version=0.2.0-alpha.2"; \
		echo "  3. Move to beta:    make pre-release version=0.2.0-beta.1"; \
		echo "  4. Move to rc:      make pre-release version=0.2.0-rc.1"; \
		echo "  5. Final release:   make release bump=pre (from rc) OR bump=patch/minor (from stable)"; \
		exit 1; \
	fi
	@echo "${INFO} Preparing pre-release $(version)... 🧪"
	@make clean
	@make build
	@uv run bump-my-version bump --new-version $(version) pre
	@uv lock --upgrade-package litestar-asyncapi >/dev/null 2>&1
	@echo "${OK} Pre-release $(version) complete 🧪"
	@echo ""
	@echo "${INFO} Next steps:"
	@echo "  1. Push: git push origin HEAD"
	@echo "  2. Create a GitHub pre-release: gh release create v$(version) --prerelease --title 'v$(version)'"
	@echo "  3. This will publish to PyPI with pre-release tags"

# =============================================================================
# Documentation
# =============================================================================

.PHONY: docs
docs:                                             ## Build documentation
	@echo "${INFO} Building docs... 📚"
	@uv run sphinx-build -b html docs docs/_build/html
	@echo "${OK} Docs build complete 📚"

.PHONY: docs-linkcheck
docs-linkcheck:                                   ## Check documentation links
	@echo "${INFO} Checking docs links... 📚"
	@uv run sphinx-build -b linkcheck docs docs/_build/linkcheck
	@echo "${OK} Docs linkcheck complete 📚"

.PHONY: docs-clean
docs-clean:                                       ## Clean documentation artifacts
	@echo "${INFO} Cleaning docs artifacts... 📚"
	@rm -rf docs/_build docs-build >/dev/null 2>&1
	@echo "${OK} Docs artifacts cleaned 📚"

.PHONY: docs-audit
docs-audit:                                       ## Audit documentation structure and terminology
	@echo "${INFO} Auditing docs... 📚"
	@if [ -f tools/docs_audit.py ]; then \
		uv run python tools/docs_audit.py; \
	else \
		echo "${INFO} tools/docs_audit.py not found, skipping"; \
	fi
	@echo "${OK} Docs audit complete 📚"

# =============================================================================
# Validation Targets
# =============================================================================

.PHONY: validate-examples
validate-examples:                                  ## Validate docs/examples marker blocks
	@echo "${INFO} Validating doc example markers... 🔍"
	@uv run python tools/ci/validate_doc_markers.py
	@echo "${OK} Doc example markers valid ✨"

.PHONY: validate-pep723
validate-pep723:                                    ## Validate PEP 723 blocks in runnable examples
	@echo "${INFO} Validating PEP 723 script blocks... 🔍"
	@uv run python tools/ci/validate_pep723_blocks.py
	@echo "${OK} PEP 723 blocks valid ✨"

# =============================================================================
# Cleaning and Maintenance
# =============================================================================

.PHONY: clean
clean:                                              ## Cleanup temporary build artifacts
	@echo "${INFO} Cleaning working directory... 🧹"
	@rm -rf .pytest_cache .ruff_cache .hypothesis build/ dist/ .eggs/ .coverage coverage.xml coverage.json htmlcov/ .pytest_cache src/tests/.pytest_cache src/tests/**/.pytest_cache .mypy_cache >/dev/null 2>&1
	@find . -name '*.egg-info' -exec rm -rf {} + >/dev/null 2>&1
	@find . -type f -name '*.egg' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyc' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyo' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*~' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '__pycache__' -exec rm -rf {} + >/dev/null 2>&1
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} + >/dev/null 2>&1
	@echo "${OK} Working directory cleaned ✨"

# =============================================================================
# Testing and Quality Checks
# =============================================================================

.PHONY: test
test:                                              ## Run the tests
	@echo "${INFO} Running test cases... 🧪"
	@uv run pytest src/tests
	@echo "${OK} Tests complete 🧪"

.PHONY: test-all
test-all: test                                     ## Run all tests

.PHONY: coverage
coverage:                                          ## Run tests with coverage report
	@echo "${INFO} Running tests with coverage... 🧪"
	@uv run pytest src/tests --cov -n auto
	@uv run coverage html >/dev/null 2>&1
	@uv run coverage xml >/dev/null 2>&1
	@echo "${OK} Coverage report generated 🧪"

# -----------------------------------------------------------------------------
# Type Checking
# -----------------------------------------------------------------------------

.PHONY: mypy
mypy:                                              ## Run mypy
	@echo "${INFO} Running mypy... 🔍"
	@uv run mypy
	@echo "${OK} Mypy checks passed ✨"

.PHONY: mypy-nocache
mypy-nocache:                                      ## Run Mypy without cache
	@echo "${INFO} Running mypy without cache... 🔍"
	@uv run mypy
	@echo "${OK} Mypy checks passed ✨"

.PHONY: pyright
pyright:                                           ## Run pyright
	@echo "${INFO} Running pyright... 🔍"
	@uv run pyright
	@echo "${OK} Pyright checks passed ✨"

.PHONY: type-check
type-check: mypy pyright                           ## Run all type checking

# -----------------------------------------------------------------------------
# Linting and Formatting
# -----------------------------------------------------------------------------

WORKING_TREE_FILES = $$(git ls-files --cached --others --exclude-standard 2>/dev/null)

.PHONY: prek
prek:                                               ## Run prek hooks
	@echo "${INFO} Running prek checks... 🔍"
	@files="${WORKING_TREE_FILES}"; \
	if [ -n "$$files" ]; then \
		uvx prek run --show-diff-on-failure --color=always --files $$files; \
	else \
		uvx prek run --show-diff-on-failure --color=always --all-files; \
	fi
	@echo "${OK} prek checks passed ✨"

.PHONY: pre-commit
pre-commit: prek                                   ## Run prek hooks (alias for pre-commit)

.PHONY: zizmor
zizmor:                                             ## Run zizmor workflow security scanner
	@echo "${INFO} Running zizmor workflow security checks... 🛡️"
	@if [ -d ".github/workflows" ]; then \
		uvx zizmor .github/workflows; \
	else \
		echo "${WARN} No .github/workflows directory found"; \
	fi
	@echo "${OK} zizmor workflow checks passed ✨"

.PHONY: slotscheck
slotscheck:                                        ## Run slotscheck
	@echo "${INFO} Running slots check... 🔍"
	@uv run slotscheck src/litestar_asyncapi/
	@echo "${OK} Slots check passed ✨"

.PHONY: fix
fix:                                               ## Fix linting issues
	@echo "${INFO} Fixing linting issues... 🔍"
	@uv run ruff check --fix --unsafe-fixes .
	@uv run ruff format .
	@echo "${OK} Linting issues fixed ✨"

.PHONY: lint
lint: prek type-check slotscheck zizmor validate-examples validate-pep723 ## Run all linting checks

.PHONY: check-all
check-all: lint test-all coverage                  ## Run all checks (lint, test, coverage)

.PHONY: validate-asyncapi
validate-asyncapi: export-asyncapi-fixture          ## Validate offline AsyncAPI contracts and Draft07 payloads
	@npm run validate:asyncapi
	@node tools/validate_asyncapi.mjs .tmp/asyncapi-fixture.json

.PHONY: export-asyncapi-fixture
export-asyncapi-fixture:                           ## Export a headless application contract for the official gate
	@mkdir -p .tmp
	@uv run litestar --app-dir src --app tests.fixtures.apps.cli:app asyncapi export --output .tmp/asyncapi-fixture.json --overwrite

.PHONY: js-build js-test browser-test
js-build:                                          ## Build packaged browser assets
	@npm run build

js-test:                                           ## Test rendering-view transformations
	@npm test

browser-test:                                      ## Test packaged documentation in Chromium
	@npm run test:browser
