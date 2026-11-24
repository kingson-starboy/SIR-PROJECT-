.PHONY: help install lint format test run docker-build docker-run clean

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit
PYTEST = $(VENV)/bin/pytest
RUFF = $(VENV)/bin/ruff

help:
	@echo "Disease Spread Prediction System - Developer Tasks"
	@echo "---------------------------------------------------"
	@echo "make install      : Create venv and install dependencies"
	@echo "make lint         : Run Ruff code quality linter"
	@echo "make format       : Reformat source code with Ruff"
	@echo "make test         : Run automated test suite with pytest"
	@echo "make run          : Start Streamlit web application"
	@echo "make docker-build : Build production Docker container image"
	@echo "make docker-run   : Run containerized application on port 8501"
	@echo "make clean        : Remove Python bytecode and cache files"

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

lint:
	$(RUFF) check .

format:
	$(RUFF) format .

test:
	$(PYTEST) -v

run:
	$(STREAMLIT) run app.py

docker-build:
	docker build -t sir-epidemic-simulator:latest .

docker-run:
	docker run -p 8501:8501 sir-epidemic-simulator:latest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
