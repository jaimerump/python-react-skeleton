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

## Local dev with Tilt (one command)

`tilt up` runs the whole stack in Docker with hot reload on backend + frontend,
LocalStack-provisioned SQS, and the worker:

```bash
./scripts/generate-env.sh   # render .env (copies ~/.app/.env if present, else .env.template)
tilt up                     # db -> migrations -> api -> ui, plus localstack -> worker
```

Then: Tilt UI `http://localhost:10350`, API `http://localhost:8000`, UI `http://localhost:5173`.

Run several isolated stacks side-by-side (each gets its own ports, containers, and
volumes) — handy for parallel branches/agents:

```bash
INSTANCE=2 tilt up          # API :8100, UI :5273, Tilt UI :10450
./scripts/tilt-auto.sh      # auto-pick the first free instance and launch
./scripts/tilt-cleanup.sh 2 # tear down instance 2 (-v also drops its volumes)
./scripts/tilt-cleanup-all.sh --dry-run   # preview a full sweep
```

Prereqs: Docker, [Tilt](https://tilt.dev), `uv`, Node 22, AWS CLI. Opt out of LocalStack
with `tilt up -- --no-localstack`.

## Getting started (host, without Docker)

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
