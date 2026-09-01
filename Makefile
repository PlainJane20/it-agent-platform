.PHONY: install lint format test check run build

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -e '.[dev]'

lint:
	$(BIN)/ruff check .

format:
	$(BIN)/ruff format .
	$(BIN)/ruff check --fix .

test:
	$(BIN)/pytest --cov=it_agent_platform --cov-report=term-missing

check: lint test build

run:
	$(BIN)/uvicorn it_agent_platform.api:app --reload

build:
	$(BIN)/python -m build

