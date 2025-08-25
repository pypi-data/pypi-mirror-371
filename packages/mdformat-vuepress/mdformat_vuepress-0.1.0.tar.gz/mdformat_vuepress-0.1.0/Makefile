.PHONY: help install install-dev test test-verbose clean build publish-test publish lint format check

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in current environment"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  publish-test - Publish to TestPyPI"
	@echo "  publish      - Publish to PyPI"
	@echo "  lint         - Run linting (if configured)"
	@echo "  format       - Format code (if configured)"
	@echo "  check        - Run all checks (test + lint)"

# Installation targets
install:
	uv sync

install-dev:
	uv sync --extra test

# Test targets
test: install-dev
	uv run pytest tests/

test-verbose: install-dev
	uv run pytest tests/ -v

test-integration: install-dev build
	uv run pytest tests/test_installation.py -v
	uv run python scripts/test_wheel_install.py

# Build and publish targets
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	uv build

publish-test: build
	uv publish --repository testpypi

publish: build
	uv publish

# Code quality targets (optional - add tools as needed)
lint:
	@echo "Add your preferred linter here (ruff, flake8, etc.)"

format:
	@echo "Add your preferred formatter here (black, ruff format, etc.)"

check: test lint
	@echo "All checks passed!"