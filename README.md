# Studeal

A website that collects student discounts and events in Lviv: cafés, coworkings, gyms, concerts and workshops that give a discount for a student ID. After signing in, students browse deals and events by category, filter places of their university (UCU), search deals and save the ones they like.

**Team:** Yuliia Yakymiv, Yuliia Dub, Khrystyna Shymushovska

## Repository structure

```
backend/    FastAPI + PostgreSQL API: app/ (code), alembic/ (migrations), tests/
frontend/   React + Vite website, sign-in with Amazon Cognito
infra/      Deployment
docs/       Demo report, seed data (docs/data/*.csv)
README.md   This file
```

## How to run locally

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/), `make` and [Node.js](https://nodejs.org) 20.19+ or 22.12+. On Windows run the commands in a WSL terminal and turn on *Settings → Resources → WSL integration* in Docker Desktop.

**1. Backend and database**

```sh
make up      # creates .env from .env.example, builds and starts the database and the API
make seed    # loads deals and events from docs/data/*.csv
```

Check: http://localhost:8000/api/health → `{"status":"ok"}`. All endpoints: http://localhost:8000/api/docs.

**2. Frontend** (second terminal)

```sh
cd frontend
cp .env.example .env.local   # local mode: sign-in is skipped
npm install
npm run dev
```

Open http://localhost:5173. Requests to `/api` go to the backend on port 8000.

In local mode sign-in is skipped on both sides, so the whole site works without an AWS account.

More: [`backend/README.md`](backend/README.md) · [`frontend/README.md`](frontend/README.md).

## How to deploy

_Not deployed yet._
