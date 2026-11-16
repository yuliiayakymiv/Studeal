.DEFAULT_GOAL := help

-include .env
DB_PORT ?= 5432
LOCAL_DATABASE_URL := postgresql+asyncpg://studeal:studeal@localhost:$(DB_PORT)/studeal

.env:
	cp .env.example .env

help: ## List commands
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-12s %s\n", $$1, $$2}'

up: .env ## Build and start the database and the API (migrations run on start)
	docker compose up -d --build

down: ## Stop everything
	docker compose down

logs: ## Follow logs (one service: make logs s=backend)
	docker compose logs -f $(s)

ps: ## Show running containers
	docker compose ps

seed: ## Load deals and events from docs/data/*.csv (safe to re-run)
	docker compose exec backend python -m app.seed

test: ## Run backend tests (against the studeal_test database)
	docker compose exec backend pytest -v

migrate: ## Apply database migrations
	docker compose exec backend alembic upgrade head

migration: ## Generate a migration after changing models: make migration m="add something"
	@test -n "$(m)" || (echo 'Usage: make migration m="message"' && exit 1)
	cd backend && DATABASE_URL=$(LOCAL_DATABASE_URL) uv run alembic revision --autogenerate -m "$(m)"

psql: ## Open a psql shell in the database
	docker compose exec db psql -U studeal -d studeal

install: ## Install local backend dependencies (uv)
	cd backend && uv sync

dev-backend: .env ## Run the API locally with reload (database runs in Docker)
	docker compose up -d db
	cd backend && DATABASE_URL=$(LOCAL_DATABASE_URL) uv run alembic upgrade head
	cd backend && DATABASE_URL=$(LOCAL_DATABASE_URL) uv run uvicorn app.main:app --reload --port 8000

lint: ## Check backend code style (ruff)
	cd backend && uv run ruff check . && uv run ruff format --check .

format: ## Fix backend code style (ruff)
	cd backend && uv run ruff check --fix . && uv run ruff format .

clean: ## Stop and delete the database volume
	docker compose down -v
