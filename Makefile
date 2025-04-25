# Variables
PYTHON := python
POETRY := poetry
PROJECT := fastapi_signoz_test
VERSION_TAG ?= latest
PORT ?= 8081
HOST ?= 0.0.0.0
REGISTRY_URL = nunenuh/fastapi-signoz-test

# Colors for terminal output
BLUE := \033[34m
GREEN := \033[32m
RED := \033[31m
RESET := \033[0m

.PHONY: help install test lint format clean run docker-build docker-run docker-stop kill-port celery-worker celery-flower test-celery dev-setup celery-stop version-last version-next

# Default target
help:
	@echo "$(BLUE)Available commands:$(RESET)"
	@echo "$(GREEN)make install$(RESET)    - Install project dependencies"
	@echo "$(GREEN)make test$(RESET)       - Run tests"
	@echo "$(GREEN)make lint-all$(RESET)   - Run linting checks"
	@echo "$(GREEN)make clean$(RESET)      - Clean up temporary files"
	@echo "$(GREEN)make run$(RESET)        - Run the FastAPI application"
	@echo "$(GREEN)make docker-build$(RESET) - Build docker image"
	@echo "$(GREEN)make docker-run$(RESET)  - Run with docker compose"
	@echo "$(GREEN)make docker-stop$(RESET) - Stop docker compose"
	@echo "$(GREEN)make dev-setup$(RESET)   - Set up development environment"
	@echo "$(GREEN)make version-last$(RESET) - Get the latest version"
	@echo "$(GREEN)make version-next$(RESET) - Calculate next version number"

# Install dependencies
install:
	@echo "$(BLUE)Installing project dependencies...$(RESET)"
	$(POETRY) install --with dev

# Run tests
test:
	@echo "$(BLUE)Running tests...$(RESET)"
	$(POETRY) run pytest tests/ -v

# Run tests with coverage
test-coverage:
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(POETRY) run pytest tests/ --cov=$(PROJECT) --cov-report=term-missing

# Run pre-commit checks
lint-all:
	@echo "$(BLUE)Running pre-commit checks...$(RESET)"
	$(POETRY) run pre-commit run --all-files

# Clean up temporary files
clean:
	@echo "$(BLUE)Cleaning up temporary files...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# Run the FastAPI application
run: kill-port
	@echo "$(BLUE)Running the FastAPI application...$(RESET)"
	$(POETRY) run uvicorn src.fastapi_signoz_test.main:app --host $(HOST) --port $(PORT)

# Docker login
docker-login:
	@echo "$(BLUE)Logging in to Docker registry...$(RESET)"
	@docker login

# Update dependencies
update:
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(POETRY) update

# Docker commands
docker-build:
	@echo "Building service images version $(VERSION)..."
	docker compose -f builder/docker-compose.build.yml build webapi

# Docker push
docker-push:
	@echo "Pushing service images version $(VERSION)..."
	docker compose -f builder/docker-compose.build.yml push webapi

docker-build-push:
	make docker-build
	make docker-push

# Docker run
docker-run:
	@echo "Running service with docker compose..."
	@docker compose up

# Docker stop
docker-stop:
	@echo "Stopping service..."
	@docker compose down

# Add this new target to kill any process using the port
kill-port:
	@echo "$(BLUE)Killing any process using port $(PORT)...$(RESET)"
	-@lsof -ti:$(PORT) | xargs kill -9 2>/dev/null || true
