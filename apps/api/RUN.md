# Running the API

Use a **dedicated conda environment** (e.g. `majster`) for this project. Do all setup inside that env so **base stays empty**; do not install API dependencies in base.

You do not need `uv`; use `pip` and the conda env’s Python.

## 1. Create and activate a conda environment

```bash
conda create -n majster python=3.12 -y
conda activate majster
```

Use this env for all API work so base remains clean.

## 2. Install dependencies

From this directory (`apps/api`):

```bash
pip install -e .
```

This installs the project and its dependencies from `pyproject.toml` into the active env (majster), not base.

## 3. Run the server

From `apps/api` (with `majster` activated):

```bash
uvicorn src.main:app --reload --port 8000
```

## 4. Optional: database and env

- Ensure PostgreSQL and Redis are running (e.g. `docker compose up -d` from the monorepo root).
- Copy `.env.example` to `.env` and set `DATABASE_URL`, LiveKit keys, and `CORS_ORIGINS` as needed.

API docs: http://localhost:8000/docs
