.DEFAULT_GOAL := help

.env:
	cp .env.example .env

help: ## List commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-12s %s\n", $$1, $$2}'

up: .env ## Build and start the database and the API
	docker compose up -d --build

down: ## Stop everything
	docker compose down

logs: ## Follow logs (one service: make logs s=backend)
	docker compose logs -f $(s)

ps: ## Show running containers
	docker compose ps

psql: ## Open a psql shell in the database
	docker compose exec db psql -U studeal -d studeal

clean: ## Stop and delete the database volume
	docker compose down -v
