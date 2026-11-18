# Studeal

A website that collects student discounts and events in Lviv: cafés, coworkings, gyms, concerts and workshops that give a discount for a student ID.

**Team:** Yuliia Yakymiv, Yuliia Dub, Khrystyna Shymushovska

**Live demo:** https://d1lp3tn7jna3tf.cloudfront.net

## Repository structure

```
backend/    FastAPI + PostgreSQL API: app/ (code), alembic/ (migrations), tests/
frontend/   The website users see (React + Vite + Tailwind + Cognito OIDC)
infra/      Deployment on AWS (eu-central-1): infra/aws/ scripts + infra/auth.yml
docs/       Demo report (docs/report.md), seed data (docs/data/*.csv)
README.md   This file
```

## How to run

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) and `make` (on Windows: run the commands in a WSL terminal and turn on *Settings → Resources → WSL integration* in Docker Desktop).

```sh
make up      # creates .env from .env.example, builds and starts the database and the API
make seed    # loads deals and events from docs/data/*.csv
make         # lists all commands
```

To run the frontend locally in dev mode (proxies `/api` to `:8000`):

```sh
make install       # uv sync + npm install
make dev-frontend  # creates frontend/.env.local (local mode, no sign-in), http://localhost:5173
```

- API health check: http://localhost:8000/api/health
- API docs (try every endpoint in the browser): http://localhost:8000/api/docs

Locally sign-in is off: every request acts as one test user. To turn it on, set `COGNITO_ISSUER` and `COGNITO_CLIENT_ID` in `.env` (and `VITE_COGNITO_*` in `frontend/.env.local`, see `frontend/README.md`).

Backend details (all commands, API endpoints, sign-in): [`backend/README.md`](backend/README.md).

## Deploy (AWS `eu-central-1`)

Studeal runs on the same AWS architecture as `spry` (Labs 2 & 4) in region `eu-central-1`:

```
browser ──HTTPS──▶ CloudFront ──┬─ /*      ──OAC──▶ S3 (private bucket: React SPA)
                                └─ /api/*  ──HTTP─▶ ALB :80 ─▶ ECS Fargate :8000 ─▶ RDS PostgreSQL 17 :5432
                                                                     │
                                                             Amazon Cognito (JWT auth)
```

### One-time AWS setup

Configure AWS CLI credentials (`aws configure`, region `eu-central-1`), then set a monthly budget alert and run the idempotent setup scripts in `infra/aws/`:

```sh
bash infra/aws/00-budget.sh your-email@ucu.edu.ua 5   # A1: $5 monthly budget alert
bash infra/aws/setup-all.sh                           # A2–A4: runs 01-network .. 08-api-auth
```

Or step by step:

| Step | Command | What it creates |
|---|---|---|
| A1 | `bash infra/aws/00-budget.sh <email> 5` | AWS Budget alert (80% actual / 100% forecasted) |
| A2.1 | `bash infra/aws/01-network.sh` | Default VPC + security groups (`studeal-alb` → `studeal-ecs` → `studeal-rds`) |
| A2.2 | `bash infra/aws/02-database.sh` | Private RDS PostgreSQL 17 (`db.t4g.micro`) + `DATABASE_URL` in SSM Parameter Store |
| A2.3 | `bash infra/aws/03-image.sh` | ECR repo `studeal-backend` + initial Docker image (with `docs/data/*.csv` bundled) |
| A2.4 | `bash infra/aws/04-ecs.sh` | ECS Fargate cluster `studeal`, task definition, ALB `studeal-alb`, service `studeal-backend` |
| A2.5 | `bash infra/aws/05-frontend.sh` | Private S3 bucket + CloudFront distribution (`/*` → S3, `/api/*` → ALB) + initial frontend deploy |
| A2.6 | `bash infra/aws/06-oidc.sh` | GitHub Actions OIDC provider and deploy role `studeal-github-deploy` |
| A3 | `make deploy-auth` (`07-auth.sh`) | CloudFormation stack `studeal-auth` (`infra/auth.yml`: Cognito User Pool email + password), CloudFront SPA routing function, frontend rebuild with `VITE_COGNITO_*` |
| A3/A4 | `make deploy-api-auth` (`08-api-auth.sh`) | Sets `COGNITO_ISSUER` and `COGNITO_CLIENT_ID` on the ECS task definition and rolls the service |

### Deploying updates & seeding RDS

```sh
make deploy-backend              # Build image (bundling docs/data/*.csv), push to ECR as :<git-sha>, roll ECS (auto-migrates & seeds RDS)
make deploy-frontend             # Build frontend with VITE_COGNITO_*, sync to S3, invalidate CloudFront
make seed-rds                    # Optional: run a one-off ECS Fargate task to re-run migrations + seed on RDS
make rollback-backend TAG=<sha>  # Roll back ECS service to an earlier image tag in ECR
make teardown                    # After grading (A9): delete all AWS resources so AWS stops billing
```

Full runbook, architecture details, and troubleshooting: [`infra/README.md`](infra/README.md).
