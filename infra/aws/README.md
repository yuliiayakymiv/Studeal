# AWS scripts (`infra/aws/`)

See the full deployment runbook in [`infra/README.md`](../README.md).

| Script | Purpose |
|---|---|
| `00-budget.sh` | Create monthly AWS cost budget alert (A1) |
| `01-network.sh` | Default VPC lookup, security groups `studeal-alb` → `studeal-ecs` → `studeal-rds` (A2) |
| `02-database.sh` | RDS PostgreSQL 17 `db.t4g.micro` (private), `DATABASE_URL` in SSM `/studeal/DATABASE_URL` (A2) |
| `03-image.sh` | ECR repository `studeal-backend`, first backend image `:<commit sha>` with seed CSVs (A2) |
| `04-ecs.sh` | Execution role, task definition, cluster, ALB + target group, Fargate service (A2) |
| `05-frontend.sh` | Private S3 bucket, CloudFront (`/*` → S3, `/api/*` → ALB), first frontend deploy (A2) |
| `06-oidc.sh` | GitHub OIDC provider + deploy role `studeal-github-deploy` (A2) |
| `07-auth.sh` (`make deploy-auth`) | Deploy `infra/auth.yml` Cognito stack (`studeal-auth`), CloudFront Function `studeal-spa-routes`, rebuild frontend with `VITE_COGNITO_*` (A3) |
| `08-api-auth.sh` (`make deploy-api-auth`) | Configure `COGNITO_ISSUER` & `COGNITO_CLIENT_ID` on ECS service (A3/A4) |
| `deploy-backend.sh` (`make deploy-backend`) | Build image with `docs/data/*.csv`, push to ECR, roll ECS service (A4) |
| `release-backend.sh` (`make release-backend`) | Point ECS at an existing image tag in ECR (A4) |
| `deploy-frontend.sh` (`make deploy-frontend`) | Build frontend with `VITE_COGNITO_*`, sync to S3, invalidate CloudFront (A4) |
| `seed.sh` (`make seed-rds`) | Run one-off ECS Fargate task to migrate and seed RDS (A4) |
| `setup-all.sh` | Run `01-network` through `08-api-auth` sequentially |
| `teardown.sh` (`make teardown`) | Delete all AWS resources after grading (A9) |
