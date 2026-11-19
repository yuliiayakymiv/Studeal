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
| GET | `/api/deals?category=coffee&university=ucu&q=кава` | token | Current deals (expired ones hidden, `?include_expired=true` for all); filter by category, university, search text (all optional) |
| GET | `/api/deals/categories` | token | Categories that have deals |
| GET | `/api/deals/{id}` | token | One deal |
| GET | `/api/events?category=quiz&university=ucu&q=квіз` | token | Upcoming events; filter by category, university, search text (`?include_past=true` for past ones too) |
| GET | `/api/events/categories` | token | Categories that have events |
| GET | `/api/stats` | token | Usage totals for the report: users, users who came back, saves, top saved deals |
| GET | `/api/me` | token | The signed-in user (`id` = Cognito `sub`) |
| GET | `/api/me/saved` | token | The user's saved deals |
| POST / DELETE | `/api/me/saved/{id}` | token | Save / unsave a deal |
| GET | `/api/me/saved-events` | token | The user's saved events |
| POST / DELETE | `/api/me/saved-events/{id}` | token | Save / unsave an event |

Everything except `/api/health` needs sign-in, as in spry: the site can have a public landing page, but deals and events load only after sign-in. Every signed-in call also counts the user for `/api/stats`. Ids are UUIDs.

Sign-in uses Amazon Cognito (as in spry): the frontend sends the access token as `Authorization: Bearer <token>`, and the API checks its signature, expiry, issuer and app client.

## Configuration

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:password@host:5432/db` |
| `CORS_ORIGINS` | Frontend URLs allowed to call the API, comma-separated |
| `COGNITO_ISSUER` | `https://cognito-idp.eu-central-1.amazonaws.com/<user pool id>`; empty = sign-in off |
| `COGNITO_CLIENT_ID` | Cognito app client id |

The container listens on port `8000` and applies migrations on start.
