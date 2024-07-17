env = env PATH="${bin}:$$PATH"

ifdef DOCKER
  RUN_PREFIX := docker compose run --rm service
else
  RUN_PREFIX := . .venv/bin/activate && ${env}
endif

.SILENT: help
all: help


lint: ## Check for linting errors
	$(RUN_PREFIX) ruff check

lint-fix: ## Fix linting errors
	$(RUN_PREFIX) ruff check --fix --show-fixes

type-check: ## Check for typing errors
	$(RUN_PREFIX) mypy

safety-check: ## Check for security vulnerabilities
	$(RUN_PREFIX) safety check

spelling-check: ## Check spelling mistakes
	$(RUN_PREFIX) codespell -L selectin .

spelling-fix: ## Fix spelling mistakes
	$(RUN_PREFIX) codespell -L selectin . --write-changes --interactive=3

test: ## Runs automated tests
	$(RUN_PREFIX) pytest --cov --cov-report=term --cov-report=xml

check: lint type-check safety-check spelling-check test ## Runs all checks
fix: lint-fix spelling-fix ## Runs all fixers

help: ## Display available commands
	echo "Available make commands:"
	echo
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'