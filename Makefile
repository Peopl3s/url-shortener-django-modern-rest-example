.DEFAULT_GOAL := help
.PHONY: help \
        install install-dev \
        run run-docker stop restart logs shell \
        migrate makemigrations \
        test test-fast lint format typecheck check \
        build build-dev \
        clean clean-docker clean-all

# ─── Variables ────────────────────────────────────────────────────────────────

COMPOSE      := docker compose
COMPOSE_PROD := docker compose -f docker-compose.yml
UV           := uv run

# ─── Help ─────────────────────────────────────────────────────────────────────

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' \
	| sort

# ─── Dependencies ─────────────────────────────────────────────────────────────

install:  ## Install production dependencies
	uv sync --frozen --no-dev

install-dev:  ## Install all dependencies including dev groups
	uv sync --frozen

# ─── Local development (no Docker) ────────────────────────────────────────────

run:  ## Start Django development server locally (port 8000)
	$(UV) python manage.py runserver

migrate:  ## Apply database migrations locally
	$(UV) python manage.py migrate --noinput

makemigrations:  ## Create new migration files
	$(UV) python manage.py makemigrations

shell:  ## Open Django shell locally
	$(UV) python manage.py shell

# ─── Docker: development ──────────────────────────────────────────────────────

run-docker:  ## Build and start all services in development mode (with override)
	$(COMPOSE) up --build

run-docker-detach:  ## Same as run-docker but in background
	$(COMPOSE) up --build -d

stop:  ## Stop all running containers
	$(COMPOSE) down

restart:  ## Restart all containers
	$(COMPOSE) restart

logs:  ## Tail logs from all containers (Ctrl+C to stop)
	$(COMPOSE) logs -f

logs-web:  ## Tail logs from the web container only
	$(COMPOSE) logs -f web

shell-docker:  ## Open a shell inside the running web container
	$(COMPOSE) exec web sh

migrate-docker:  ## Run migrations inside the running Docker container
	$(COMPOSE) exec web python manage.py migrate --noinput

makemigrations-docker:  ## Create migrations inside the running Docker container
	$(COMPOSE) exec web python manage.py makemigrations

# ─── Docker: production ───────────────────────────────────────────────────────

run-prod:  ## Start in production mode (requires DJANGO_SECRET_KEY env var)
	$(COMPOSE_PROD) up --build -d

stop-prod:  ## Stop production containers
	$(COMPOSE_PROD) down

# ─── Tests ────────────────────────────────────────────────────────────────────

test:  ## Run full test suite with coverage
	$(UV) pytest

test-fast:  ## Run tests without coverage (faster feedback)
	$(UV) pytest --no-cov

test-docker:  ## Run tests inside the Docker dev container
	$(COMPOSE) exec web pytest

# ─── Code quality ─────────────────────────────────────────────────────────────

lint:  ## Check code with ruff (no fixes applied)
	$(UV) ruff check .

format:  ## Auto-format and fix code with ruff
	$(UV) ruff format .
	$(UV) ruff check --fix .

typecheck:  ## Run mypy type checking
	$(UV) mypy .

check: lint typecheck test  ## Run all checks: lint + typecheck + tests

# ─── Build ────────────────────────────────────────────────────────────────────

build:  ## Build the production Docker image
	$(COMPOSE_PROD) build

build-dev:  ## Build the development Docker image (with dev dependencies)
	$(COMPOSE) build

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean:  ## Remove Python cache files and test artifacts
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml .coverage

clean-docker:  ## Remove project containers and volumes (DESTRUCTIVE: deletes DB data)
	$(COMPOSE) down -v --remove-orphans

clean-all: clean clean-docker  ## Full cleanup: cache files + containers + volumes
