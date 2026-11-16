# Studeal

A website that collects student discounts and events in Lviv: cafés, coworkings, gyms, concerts and workshops that give a discount for a student ID.

**Team:** Yuliia Yakymiv, Yuliia Dub, Khrystyna Shymushovska

## Repository structure

```
backend/    API and database
frontend/   The website users see
infra/      Deployment and local setup
docs/       Demo report
README.md   This file
```

## How to run

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) and `make` (on Windows, run the commands in a WSL terminal).

```sh
make up      # creates .env from .env.example, builds and starts the database and the API
make         # lists all commands
```

- API health check: http://localhost:8000/api/health
- API docs: http://localhost:8000/api/docs

## How to deploy

_TODO_
