.PHONY: help install dev test lint format clean run docker-build docker-up docker-down migrate

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements-dev.txt || echo "No requirements-dev.txt found"
	pip install -e .

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	pytest-watch tests/

lint: ## Run linters
	flake8 src tests
	pylint src
	mypy src

format: ## Format code with black
	black src tests

format-check: ## Check code formatting
	black --check src tests

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf dist/
	rm -rf build/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .tox/

run: ## Run the application
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the application in production mode
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

docker-build: ## Build Docker image
	docker build -t v402-facilitator:latest .

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f facilitator

docker-restart: ## Restart Docker containers
	docker-compose restart

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

shell: ## Start Python shell
	python -i -c "from src.main import *; import IPython; IPython.embed()"

db-shell: ## Open database shell
	docker-compose exec postgres psql -U v402 -d v402

redis-shell: ## Open Redis shell
	docker-compose exec redis redis-cli

logs: ## View application logs
	tail -f logs/*.log

requirements: ## Update requirements
	pip freeze > requirements.txt

init-db: ## Initialize database
	python scripts/init_db.py

reset-db: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v && \
		docker-compose up -d postgres redis && \
		sleep 5 && \
		python scripts/init_db.py; \
	fi

health: ## Check application health
	curl http://localhost:8000/health

metrics: ## View Prometheus metrics
	curl http://localhost:8000/metrics

docs: ## Generate API documentation
	@echo "API documentation at http://localhost:8000/docs"

