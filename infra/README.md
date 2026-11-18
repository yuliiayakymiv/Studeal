# AWS Infrastructure & Deployment Runbook (`eu-central-1`)

Studeal uses the same AWS architecture as `spry` (Lab 2 + Lab 4) in `eu-central-1`. All setup and deployment scripts live in [`infra/aws/`](aws/) and the Cognito User Pool template lives in [`infra/auth.yml`](auth.yml).

```
browser ──HTTPS──▶ CloudFront ──┬─ /*      ──OAC──▶ S3 (private bucket)
                                └─ /api/*  ──HTTP─▶ ALB :80 ─▶ ECS Fargate task :8000 ─▶ RDS :5432
GitHub Actions ──OIDC──▶ IAM role studeal-github-deploy ──▶ ECR push · ECS update · S3 sync · CF invalidation
```

## Prerequisites

Install and configure on your machine (macOS, Linux, or Windows Git Bash / WSL):
- `aws` CLI v2 (`aws configure` with default region `eu-central-1`)
- `docker` (running)
- `node` & `npm` (for building `frontend/`)
- `jq`, `curl`, `openssl`, `make`

Every script in `infra/aws/` is idempotent (safe to re-run) and saves created resource IDs in `infra/aws/.state` (git-ignored).

## Step-by-Step Runbook

### 1. Budget Alert (A1)

```sh
bash infra/aws/00-budget.sh your-email@ucu.edu.ua 5
```

### 2. Core Stack: VPC, RDS, ECR, ECS Fargate, ALB, S3 + CloudFront (A2)

Run the entire stack setup with a single command:

```sh
bash infra/aws/setup-all.sh
```

Or execute each script individually:

| Script | Creates | Estimated Time |
|---|---|---|
| `bash infra/aws/01-network.sh` | Default VPC lookup + 3 chained security groups: `studeal-alb` → `studeal-ecs` → `studeal-rds` | 1 min |
| `bash infra/aws/02-database.sh` | Private RDS PostgreSQL 17 (`db.t4g.micro`) + `/studeal/DB_PASSWORD` + `/studeal/DATABASE_URL` in SSM | 10–15 min |
| `bash infra/aws/03-image.sh` | ECR repository `studeal-backend` + initial `linux/amd64` Docker image with `docs/data/*.csv` | 3–5 min |
| `bash infra/aws/04-ecs.sh` | IAM role, log group `/ecs/studeal-backend`, task definition, cluster `studeal`, ALB `studeal-alb`, Fargate service | 5–8 min |
| `bash infra/aws/05-frontend.sh` | Private S3 bucket `studeal-frontend-<account-id>`, CloudFront OAC & distribution, initial frontend deploy | 10–15 min |
| `bash infra/aws/06-oidc.sh` | GitHub OIDC provider + IAM role `studeal-github-deploy` | 1 min |

### 3. Cognito Authentication (A3)

```sh
make deploy-auth      # runs bash infra/aws/07-auth.sh
make deploy-api-auth  # runs bash infra/aws/08-api-auth.sh
```

At the end of `07-auth.sh`, the script prints the exact values to share with teammates:
- **For Person 2 (Frontend):** `VITE_COGNITO_ISSUER`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_DOMAIN`
- **For Person 1 (Backend):** `UserPoolId`, `COGNITO_ISSUER`, `COGNITO_CLIENT_ID`

### 4. Continuous Deployment, Migrations & Seeding RDS (A4)

- `make deploy-backend` — bundles `docs/data/*.csv`, builds & pushes `backend/Dockerfile`, rolls ECS service (container runs `alembic upgrade head && python -m app.seed` on startup).
- `make seed-rds` — runs an on-demand one-off ECS Fargate task to migrate and seed RDS.
- `make deploy-frontend` — builds Vite bundle with `VITE_COGNITO_*`, syncs to S3, invalidates CloudFront.
- `make rollback-backend TAG=<sha>` — rolls back ECS to an earlier ECR image tag.

### 5. Teardown After Grading (A9)

```sh
make teardown   # or: bash infra/aws/teardown.sh
```
Then disable & delete the CloudFront distribution, delete CloudFront Function `studeal-spa-routes`, and delete security groups `studeal-alb`, `studeal-ecs`, `studeal-rds` once RDS deletion finishes.
