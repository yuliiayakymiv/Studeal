.DEFAULT_GOAL := help

-include .env
DB_PORT ?= 5432
LOCAL_DATABASE_URL := postgresql+asyncpg://studeal:studeal@localhost:$(DB_PORT)/studeal

.PHONY: help up down logs ps seed test migrate migration psql install dev-backend dev-frontend \
	lint format clean deploy-backend release-backend rollback-backend deploy-frontend \
	deploy-auth deploy-api-auth seed-rds teardown

.env:
	cp .env.example .env

help: ## List commands
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-16s %s\n", $$1, $$2}'

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

install: ## Install local dependencies (uv + npm)
	cd backend && uv sync
	cd frontend && npm install

dev-backend: .env ## Run the API locally with reload (database runs in Docker)
	docker compose up -d db
	cd backend && DATABASE_URL=$(LOCAL_DATABASE_URL) uv run alembic upgrade head
	cd backend && DATABASE_URL=$(LOCAL_DATABASE_URL) uv run uvicorn app.main:app --reload --port 8000

frontend/.env.local:
	cp frontend/.env.example frontend/.env.local

dev-frontend: frontend/.env.local ## Run Vite dev server on http://localhost:5173 (proxies /api to :8000)
	cd frontend && npm run dev

lint: ## Check backend code style (ruff)
	cd backend && uv run ruff check . && uv run ruff format --check .

format: ## Fix backend code style (ruff)
	cd backend && uv run ruff check --fix . && uv run ruff format .

clean: ## Stop and delete the database volume
	docker compose down -v

AWS_REGION      ?= eu-central-1
ECR_REPOSITORY  ?= studeal-backend
ECS_CLUSTER     ?= studeal
ECS_SERVICE     ?= studeal-backend
ECS_TASK_FAMILY ?= studeal-backend
CONTAINER_NAME  ?= studeal-backend
S3_BUCKET       ?=
CLOUDFRONT_DISTRIBUTION_ID ?=
VITE_API_URL    ?=
IMAGE_TAG       ?= $(shell git rev-parse HEAD)

DEPLOY_ENV := AWS_REGION="$(AWS_REGION)" ECR_REPOSITORY="$(ECR_REPOSITORY)" \
	ECS_CLUSTER="$(ECS_CLUSTER)" ECS_SERVICE="$(ECS_SERVICE)" ECS_TASK_FAMILY="$(ECS_TASK_FAMILY)" \
	CONTAINER_NAME="$(CONTAINER_NAME)" IMAGE_TAG="$(IMAGE_TAG)" S3_BUCKET="$(S3_BUCKET)" \
	CLOUDFRONT_DISTRIBUTION_ID="$(CLOUDFRONT_DISTRIBUTION_ID)" VITE_API_URL="$(VITE_API_URL)"

deploy-backend: ## Build backend image (with seed CSVs), push to ECR as :<sha>, roll ECS service
	$(DEPLOY_ENV) bash infra/aws/deploy-backend.sh

release-backend: ## Point ECS at an image already in ECR (IMAGE_TAG=<sha>)
	$(DEPLOY_ENV) bash infra/aws/release-backend.sh

rollback-backend: ## Redeploy an earlier image, no rebuild: make rollback-backend TAG=<sha>
	@test -n "$(TAG)" || (echo 'Usage: make rollback-backend TAG=<commit-sha>' && exit 1)
	$(MAKE) release-backend IMAGE_TAG=$(TAG)

deploy-frontend: ## Build frontend with VITE_COGNITO_*, sync to S3, invalidate CloudFront
	$(DEPLOY_ENV) bash infra/aws/deploy-frontend.sh

deploy-auth: ## Deploy Cognito User Pool (infra/auth.yml), CloudFront SPA routing, rebuild frontend
	bash infra/aws/07-auth.sh

deploy-api-auth: ## Set COGNITO_ISSUER & COGNITO_CLIENT_ID on ECS so API verifies Cognito tokens
	bash infra/aws/08-api-auth.sh

seed-rds: ## Run a one-off ECS Fargate task to apply migrations and seed docs/data/*.csv on RDS
	bash infra/aws/seed.sh

teardown: ## Delete all AWS resources after grading so AWS stops billing
	bash infra/aws/teardown.sh
