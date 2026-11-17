# Studeal

A website that collects student discounts and events in Lviv: cafés, coworkings, gyms, concerts and workshops that give a discount for a student ID.

**Team:** Yuliia Yakymiv, Yuliia Dub, Khrystyna Shymushovska

## Repository structure

```
backend/    FastAPI + PostgreSQL API: app/ (code), alembic/ (migrations), tests/
frontend/   The website users see
infra/      Deployment (AWS)
docs/       Demo report, seed data (docs/data/*.csv)
README.md   This file
```

## How to run

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) and `make` (on Windows: run the commands in a WSL terminal and turn on *Settings → Resources → WSL integration* in Docker Desktop).

```sh
make up      # creates .env from .env.example, builds and starts the database and the API
make seed    # loads deals and events from docs/data/*.csv
make         # lists all commands
```

- API health check: http://localhost:8000/api/health
- API docs (try every endpoint in the browser): http://localhost:8000/api/docs

Locally sign-in is off: every request acts as one test user. To turn it on, set `COGNITO_ISSUER` and `COGNITO_CLIENT_ID` in `.env`.

Backend details (all commands, API endpoints, sign-in): [`backend/README.md`](backend/README.md).

## How to deploy

_TODO_
