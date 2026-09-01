# app

Backend built on **FastAPI + `svcs` DI + SQLAlchemy/Alembic on Postgres + a separate
SQS-polling worker**, organized as three layers so the API and worker are thin entry
points over a shared, framework-agnostic core.

## Layout

```
src/app/
├── lib/      # shared core — imports NEITHER api NOR worker
├── api/      # FastAPI app (imports lib only)
└── worker/   # SQS worker (imports lib only)
```

The `api → lib`, `worker → lib`, `lib → neither` boundary is enforced by import-linter
(`uv run lint-imports`). Keep it green.

## Getting started

```bash
uv sync                                    # install deps into .venv
cp .env.example .env                       # configure (defaults target local docker)
docker compose up -d                       # Postgres + LocalStack (SQS)
uv run alembic upgrade head                # create the schema
uv run uvicorn app.api.main:app --reload   # API at http://localhost:8000
uv run python -m app.worker                # worker (needs APP_SQS_QUEUE_URL)
```

Health checks: `GET /health` (liveness), `GET /ready` (DB reachable).

## Development

```bash
uv run pytest            # tests (spins up Postgres via testcontainers)
uv run ruff check .      # lint
uv run mypy src          # type check
uv run lint-imports      # architecture boundary check
```

## Adding a service

A service is a class extending `BaseService` + a `create_*` factory + one registration
line in `lib/service_registry.py`. Endpoints resolve it with
`await services.aget(MyService)`. Keep authorization a separate `Depends`.

## Adding an async job

See [docs/architecture/adding-an-automated-job.md](docs/architecture/adding-an-automated-job.md).
The failure modes are all silent, so follow the checklist and verify the side effect.
