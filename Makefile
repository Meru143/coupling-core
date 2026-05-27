.PHONY: dev lint type-check test build clean

dev:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

type-check:
	mypy src/ --strict

test:
	pytest tests/ -v --cov=src/coupling_core --cov-report=term-missing

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ .coverage coverage.xml
