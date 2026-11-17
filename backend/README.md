# Backend

FastAPI + PostgreSQL (async SQLAlchemy, Alembic), same setup as spry. Run everything from the repo root, see the main [README](../README.md).

## Commands

| Command | What it does |
|---|---|
| `make seed` | Load `docs/data/deals.csv` and `events.csv` (safe to re-run, updates instead of duplicating) |
| `make test` | Backend tests (run in the container against the `studeal_test` database) |
| `make logs s=backend` | Follow the API logs |
| `make migration m="..."` | Generate a migration after changing `backend/app/models.py` |
| `make psql` | Open a psql shell |
| `make dev-backend` | API on your machine with auto-reload (needs [uv](https://docs.astral.sh/uv/)); the database stays in Docker |
| `make clean` | Stop and delete the local database |

## API

| Method | Path | Auth | What |
|---|---|---|---|
| GET | `/api/health` | — | API and database are up |
| GET | `/api/deals?category=coffee&university=ucu&q=кава` | — | Deals; filter by category, university, search text (all optional) |
| GET | `/api/deals/categories` | — | Categories that have deals |
| GET | `/api/deals/{id}` | — | One deal |
| GET | `/api/events` | — | Upcoming events (`?university=ucu`, `?q=` search, `?include_past=true` for all) |
| GET | `/api/stats` | — | Usage totals for the report: users, users who came back, saves, top saved deals |
| GET | `/api/me` | token | The signed-in user (`id` = Cognito `sub`) |
| GET | `/api/me/saved` | token | The user's saved deals |
| POST / DELETE | `/api/me/saved/{id}` | token | Save / unsave a deal |

A user is counted in `/api/stats` once the site calls any `/api/me` endpoint for them (the frontend should call `GET /api/me` after sign-in).

Sign-in uses Amazon Cognito (as in spry): the frontend sends the access token as `Authorization: Bearer <token>`, and the API checks its signature, expiry, issuer and app client.

## Configuration

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:password@host:5432/db` |
| `CORS_ORIGINS` | Frontend URLs allowed to call the API, comma-separated |
| `COGNITO_ISSUER` | `https://cognito-idp.eu-central-1.amazonaws.com/<user pool id>`; empty = sign-in off |
| `COGNITO_CLIENT_ID` | Cognito app client id |

The container listens on port `8000` and applies migrations on start.
