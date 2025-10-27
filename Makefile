# v402 Multi-Language Framework Makefile
.PHONY: help install build test lint clean docker-build docker-run

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)v402 Multi-Language Framework$(RESET)"
	@echo "$(YELLOW)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Installation targets
install: install-python install-go install-java install-rust install-js ## Install all dependencies

install-python: ## Install Python SDK dependencies
	@echo "$(CYAN)Installing Python SDK dependencies...$(RESET)"
	cd clients/python && pip install -e ".[dev]"

install-go: ## Install Go SDK dependencies
	@echo "$(CYAN)Installing Go SDK dependencies...$(RESET)"
	cd clients/go && go mod download && go mod tidy

install-java: ## Install Java SDK dependencies
	@echo "$(CYAN)Installing Java SDK dependencies...$(RESET)"
	cd clients/java && mvn clean install -DskipTests

install-rust: ## Install Rust SDK dependencies
	@echo "$(CYAN)Installing Rust SDK dependencies...$(RESET)"
	cd clients/rust && cargo fetch

install-js: ## Install JavaScript Provider dependencies
	@echo "$(CYAN)Installing JavaScript Provider dependencies...$(RESET)"
	cd providers/javascript && pnpm install

# Build targets
build: build-python build-go build-java build-rust build-js ## Build all projects

build-python: ## Build Python SDK
	@echo "$(CYAN)Building Python SDK...$(RESET)"
	cd clients/python && python -m build

build-go: ## Build Go SDK
	@echo "$(CYAN)Building Go SDK...$(RESET)"
	cd clients/go && go build -o bin/v402-client ./cmd/v402

build-java: ## Build Java SDK
	@echo "$(CYAN)Building Java SDK...$(RESET)"
	cd clients/java && mvn clean package

build-rust: ## Build Rust SDK
	@echo "$(CYAN)Building Rust SDK...$(RESET)"
	cd clients/rust && cargo build --release

build-js: ## Build JavaScript Provider
	@echo "$(CYAN)Building JavaScript Provider...$(RESET)"
	cd providers/javascript && pnpm build

# Test targets
test: test-python test-go test-java test-rust test-js ## Run all tests

test-python: ## Run Python tests
	@echo "$(CYAN)Running Python tests...$(RESET)"
	cd clients/python && pytest -v --cov

test-go: ## Run Go tests
	@echo "$(CYAN)Running Go tests...$(RESET)"
	cd clients/go && go test -v -race -coverprofile=coverage.out ./...

test-java: ## Run Java tests
	@echo "$(CYAN)Running Java tests...$(RESET)"
	cd clients/java && mvn test

test-rust: ## Run Rust tests
	@echo "$(CYAN)Running Rust tests...$(RESET)"
	cd clients/rust && cargo test --all-features

test-js: ## Run JavaScript tests
	@echo "$(CYAN)Running JavaScript tests...$(RESET)"
	cd providers/javascript && pnpm test

# Lint targets
lint: lint-python lint-go lint-java lint-rust lint-js ## Run all linters

lint-python: ## Lint Python code
	@echo "$(CYAN)Linting Python code...$(RESET)"
	cd clients/python && black --check src/ && ruff check src/ && mypy src/

lint-go: ## Lint Go code
	@echo "$(CYAN)Linting Go code...$(RESET)"
	cd clients/go && golangci-lint run

lint-java: ## Lint Java code
	@echo "$(CYAN)Linting Java code...$(RESET)"
	cd clients/java && mvn checkstyle:check

lint-rust: ## Lint Rust code
	@echo "$(CYAN)Linting Rust code...$(RESET)"
	cd clients/rust && cargo clippy -- -D warnings

lint-js: ## Lint JavaScript code
	@echo "$(CYAN)Linting JavaScript code...$(RESET)"
	cd providers/javascript && pnpm lint

# Format targets
format: format-python format-go format-java format-rust format-js ## Format all code

format-python: ## Format Python code
	@echo "$(CYAN)Formatting Python code...$(RESET)"
	cd clients/python && black src/ && isort src/

format-go: ## Format Go code
	@echo "$(CYAN)Formatting Go code...$(RESET)"
	cd clients/go && go fmt ./... && goimports -w .

format-java: ## Format Java code
	@echo "$(CYAN)Formatting Java code...$(RESET)"
	cd clients/java && mvn formatter:format

format-rust: ## Format Rust code
	@echo "$(CYAN)Formatting Rust code...$(RESET)"
	cd clients/rust && cargo fmt

format-js: ## Format JavaScript code
	@echo "$(CYAN)Formatting JavaScript code...$(RESET)"
	cd providers/javascript && pnpm format

# Clean targets
clean: clean-python clean-go clean-java clean-rust clean-js ## Clean all build artifacts

clean-python: ## Clean Python build artifacts
	@echo "$(CYAN)Cleaning Python artifacts...$(RESET)"
	cd clients/python && rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find clients/python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-go: ## Clean Go build artifacts
	@echo "$(CYAN)Cleaning Go artifacts...$(RESET)"
	cd clients/go && rm -rf bin/ coverage.out

clean-java: ## Clean Java build artifacts
	@echo "$(CYAN)Cleaning Java artifacts...$(RESET)"
	cd clients/java && mvn clean

clean-rust: ## Clean Rust build artifacts
	@echo "$(CYAN)Cleaning Rust artifacts...$(RESET)"
	cd clients/rust && cargo clean

clean-js: ## Clean JavaScript build artifacts
	@echo "$(CYAN)Cleaning JavaScript artifacts...$(RESET)"
	cd providers/javascript && pnpm clean && rm -rf node_modules

# Docker targets
docker-build: ## Build all Docker images
	@echo "$(CYAN)Building Docker images...$(RESET)"
	docker build -t v402/facilitator:latest -f v402_facilitator/Dockerfile .
	docker build -t v402/python-client:latest -f clients/python/Dockerfile .
	docker build -t v402/go-client:latest -f clients/go/Dockerfile .

docker-run-facilitator: ## Run facilitator in Docker
	@echo "$(CYAN)Running facilitator...$(RESET)"
	docker-compose up -d facilitator

docker-stop: ## Stop all Docker containers
	@echo "$(CYAN)Stopping Docker containers...$(RESET)"
	docker-compose down

# Development targets
dev-python: ## Run Python development server
	cd clients/python && python -m v402_client.cli

dev-go: ## Run Go development server
	cd clients/go && go run cmd/v402/main.go

dev-js: ## Run JavaScript development server
	cd providers/javascript && pnpm dev

# Documentation targets
docs: docs-python docs-go docs-java docs-rust docs-js ## Generate all documentation

docs-python: ## Generate Python documentation
	@echo "$(CYAN)Generating Python documentation...$(RESET)"
	cd clients/python && pdoc --html --output-dir docs src/v402_client

docs-go: ## Generate Go documentation
	@echo "$(CYAN)Generating Go documentation...$(RESET)"
	cd clients/go && godoc -http=:6060

docs-java: ## Generate Java documentation
	@echo "$(CYAN)Generating Java documentation...$(RESET)"
	cd clients/java && mvn javadoc:javadoc

docs-rust: ## Generate Rust documentation
	@echo "$(CYAN)Generating Rust documentation...$(RESET)"
	cd clients/rust && cargo doc --no-deps --open

docs-js: ## Generate JavaScript documentation
	@echo "$(CYAN)Generating JavaScript documentation...$(RESET)"
	cd providers/javascript && pnpm docs

# Release targets
release-python: ## Release Python package
	@echo "$(CYAN)Releasing Python package...$(RESET)"
	cd clients/python && python -m build && twine upload dist/*

release-go: ## Tag Go release
	@echo "$(CYAN)Tagging Go release...$(RESET)"
	git tag -a clients/go/v1.0.0 -m "Release Go SDK v1.0.0"
	git push origin clients/go/v1.0.0

release-java: ## Release Java package to Maven Central
	@echo "$(CYAN)Releasing Java package...$(RESET)"
	cd clients/java && mvn clean deploy -P release

release-rust: ## Publish Rust crate
	@echo "$(CYAN)Publishing Rust crate...$(RESET)"
	cd clients/rust && cargo publish

release-js: ## Publish JavaScript packages to NPM
	@echo "$(CYAN)Publishing JavaScript packages...$(RESET)"
	cd providers/javascript && pnpm publish -r

# Benchmark targets
bench-python: ## Run Python benchmarks
	cd clients/python && pytest tests/benchmarks/ --benchmark-only

bench-go: ## Run Go benchmarks
	cd clients/go && go test -bench=. -benchmem ./...

bench-rust: ## Run Rust benchmarks
	cd clients/rust && cargo bench

# CI/CD targets
ci: lint test ## Run CI pipeline

cd: build docker-build ## Run CD pipeline

# Example targets
examples: ## Run all examples
	@echo "$(CYAN)Running examples...$(RESET)"
	$(MAKE) example-python
	$(MAKE) example-go
	$(MAKE) example-java
	$(MAKE) example-rust

example-python: ## Run Python example
	cd examples/python-ai-crawler && python main.py

example-go: ## Run Go example
	cd examples/go-indexer && go run main.go

example-java: ## Run Java example
	cd examples/java-enterprise && mvn exec:java

example-rust: ## Run Rust example
	cd examples/rust-indexer && cargo run

# All-in-one targets
all: install build test ## Install, build, and test everything

check: lint test ## Run linters and tests

.PHONY: help install install-python install-go install-java install-rust install-js \
        build build-python build-go build-java build-rust build-js \
        test test-python test-go test-java test-rust test-js \
        lint lint-python lint-go lint-java lint-rust lint-js \
        format format-python format-go format-java format-rust format-js \
        clean clean-python clean-go clean-java clean-rust clean-js \
        docker-build docker-run-facilitator docker-stop \
        docs docs-python docs-go docs-java docs-rust docs-js \
        release-python release-go release-java release-rust release-js \
        bench-python bench-go bench-rust \
        ci cd examples example-python example-go example-java example-rust \
        all check

