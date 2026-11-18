# Studeal

A website that collects student discounts and events in Lviv: cafés, coworkings, gyms, concerts and workshops that give a discount for a student ID. Students sign in, browse deals and events by category, filter places of their university (UCU), search and save deals.

**Team:** Yuliia Yakymiv, Yuliia Dub, Khrystyna Shymushovska

## Repository structure

```
backend/    FastAPI + PostgreSQL API: app/ (code), alembic/ (migrations), tests/
frontend/   React + Vite + shadcn/ui website, sign-in with Amazon Cognito
infra/      Deployment to AWS
docs/       Demo report, seed data (docs/data/*.csv)
README.md   This file
```

## How to run locally

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/), `make` and [Node.js 20+](https://nodejs.org). On Windows run the commands in a WSL terminal and turn on *Settings → Resources → WSL integration* in Docker Desktop.

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

Open http://localhost:5173. Vite forwards `/api` calls to the backend on port 8000.

Locally sign-in is off on both sides, so you can use the whole site without an AWS account. To test real sign-in, fill the Cognito values in `.env` (backend) and `frontend/.env.local` (see [`frontend/README.md`](frontend/README.md)).

More: [`backend/README.md`](backend/README.md) (commands, API, sign-in) · [`frontend/README.md`](frontend/README.md) (pages, configuration).

## How to deploy

Studeal runs on AWS in `eu-central-1`, the same setup as in the course labs:

```
browser ──HTTPS──▶ CloudFront ──▶ S3                     (frontend: built React app)
                       └── /api/* ──▶ ALB ──▶ ECS Fargate (backend container) ──▶ RDS PostgreSQL
sign-in: Amazon Cognito user pool (Hosted UI, email + password)
```

Steps (scripts and details for each step live in [`infra/`](infra/)):

1. **Cognito**: create a user pool and an app client with Hosted UI; callback and sign-out URL = the CloudFront URL.
2. **Database**: RDS PostgreSQL.
3. **Backend**: build `backend/Dockerfile`, push it to ECR, run it on ECS Fargate behind an ALB (container port `8000`, health check `/api/health`). Set `DATABASE_URL` (`postgresql+asyncpg://…` pointing at RDS), `CORS_ORIGINS` (the CloudFront URL), `COGNITO_ISSUER`, `COGNITO_CLIENT_ID`. Migrations run automatically when the container starts.
4. **Data**: run `python -m app.seed` once as a one-off ECS task to load the deals.
5. **Frontend**: set `VITE_COGNITO_ISSUER`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_DOMAIN`, run `npm run build` in `frontend/`, upload `frontend/dist/` to S3 and invalidate CloudFront. CloudFront sends `/api/*` to the ALB and everything else to S3 (unknown paths → `index.html`).

The site is then available at `https://<distribution>.cloudfront.net`. Set up an AWS Budgets alert so the free tier is not exceeded.
