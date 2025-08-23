# Makefile for django-allauth-require2fa development
.PHONY: help test lint format security install quality all clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install development dependencies
	uv sync --dev

test: ## Run Django tests with proper settings
	uv run python -m django test require2fa.tests --settings=require2fa.tests.settings --verbosity=2

lint: ## Run ruff linting checks
	uv run ruff check .

format: ## Run ruff code formatting
	uv run ruff format .

security: ## Run bandit security checks
	uv run bandit -r require2fa/ --exclude require2fa/tests/

mypy: ## Run mypy type checking
	uv run mypy require2fa/

pre-commit: ## Run pre-commit hooks on all files
	uv run pre-commit run --all-files

quality: format lint security mypy ## Run all code quality checks

all: install quality test ## Full development workflow: install deps, quality checks, and tests

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf build/ dist/ *.egg-info/

dev-setup: install ## Set up development environment
	uv run pre-commit install
	@echo "Development environment ready! Run 'make test' to verify setup."