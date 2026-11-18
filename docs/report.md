# Studeal — Demo report

## Team
Yuliia Yakymiv, Yuliia Dub, Khrystyna Shymushovska

## Links
- Repository: https://github.com/yuliiayakymiv/Studeal
- Demo (HTTPS): https://d1lp3tn7jna3tf.cloudfront.net

## Who we showed it to

## How many people tried it

## What they said

## What we changed because of it

## What we changed in the deploy (Що змінили в деплої)

Ми адаптували AWS-стек із навчального проєкту `spry` (`eu-central-1`: VPC, приватний RDS PostgreSQL 17 `db.t4g.micro`, ECR + ECS Fargate, Application Load Balancer, приватний S3 + CloudFront з Origin Access Control та Amazon Cognito) під потреби **Studeal** із такими змінами:

1. **Ізоляція ресурсів та параметрів під Studeal (`infra/aws/env.sh`, `01`–`08`):**
   - Усі мережеві групи безпеки (`studeal-alb`, `studeal-ecs`, `studeal-rds`), RDS-інстанс (`studeal-db`, база `studeal`), ECR-репозиторій (`studeal-backend`), ECS-кластер (`studeal`), сервіс (`studeal-backend`), S3-бакет (`studeal-frontend-<account-id>`) та секрети в AWS SSM Parameter Store (`/studeal/DB_PASSWORD`, `/studeal/DATABASE_URL` у форматі `postgresql+asyncpg://...?ssl=require`) переведені на окремий неймспейс `studeal`.
2. **Спрощений Cognito User Pool лише з Email + Пароль (`infra/auth.yml`, `07-auth.sh`):**
   - На відміну від `spry` (де пізніше використовувався Terraform в HCP Terraform та Google OAuth IdP), для Studeal ми використали самодостатній CloudFormation-шаблон `infra/auth.yml` (стек `studeal-auth`), який піднімає Cognito User Pool (`studeal-users`, рівень Essentials, Managed Login v2) із реєстрацією та входом за **email + пароль** і публічним PKCE-клієнтом (`studeal-web`). Це дозволяє розгорнути авторизацію однією командою `make deploy-auth` без зовнішніх OAuth-секретів Google Cloud.
   - Скрипт `07-auth.sh` автоматично виводить значення `VITE_COGNITO_ISSUER`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_DOMAIN` для фронтенду та `UserPoolId` / `COGNITO_ISSUER` для бекенду, а `deploy-frontend.sh` автоматично підтягує їх зі стека CloudFormation під час збірки Vite (`VITE_COGNITO_ISSUER` замість лише `VITE_COGNITO_AUTHORITY`).
3. **Автоматичні міграції та seed реальних знижок/подій на приватному RDS (`backend/Dockerfile`, `03-image.sh`, `deploy-backend.sh`, `seed.sh`):**
   - Оскільки RDS знаходиться у приватній групі безпеки (`studeal-rds` приймає з'єднання на порт `5432` виключно від ECS-тасків з `studeal-ecs`), прямий запуск `make seed` із локального ноутбука неможливий.
   - Ми модифікували `03-image.sh` та `deploy-backend.sh`, щоб перед `docker build` актуальні файли `docs/data/deals.csv` та `docs/data/events.csv` копіювалися в образ (`/docs/data`), а `backend/Dockerfile` при старті контейнера виконує `alembic upgrade head && python -m app.seed && uvicorn ...`. Завдяки ідемпотентності `app.seed` (`ON CONFLICT DO UPDATE`) кожен деплой бекенду автоматично оновлює схему БД та синхронізує знижки й події на RDS.
   - Додатково створено скрипт `infra/aws/seed.sh` та ціль `make seed-rds`, яка запускає одноразовий ECS Fargate task для ручного перезапуску seed на RDS.
4. **Автоматизація Budget Alert та локального деплою (`00-budget.sh`, `deploy-frontend.sh`, `Makefile`):**
   - Додано скрипт `infra/aws/00-budget.sh` для створення місячного AWS Budget Alert через AWS CLI.
   - `deploy-frontend.sh` автоматично читає `S3_BUCKET` та `CF_DIST_ID` із локального `infra/aws/.state`, тому `make deploy-frontend` та `make deploy-backend` працюють однією командою без ручного передавання змінних оточення.

## Payment / donation evidence (bonus)
