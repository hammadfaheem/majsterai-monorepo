# Running the API

The project uses **uv** for dependency management. Run all commands from the monorepo root (`monorepo/`) unless otherwise noted.

## 1. Install dependencies

From the monorepo root:

```bash
uv sync
```

## 2. Configure environment

Create `apps/api/.env` (the API always loads its `.env` from this location regardless of working directory):

```env
# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Application
ENVIRONMENT=development
DEBUG=true
```

> **Note:** The `DATABASE_URL` must be a Neon (or any PostgreSQL) connection string.
> For Neon, copy the connection string from your Neon project dashboard.
> The `channel_binding=require` parameter is automatically stripped at runtime — you can leave it in the URL if Neon adds it.

## 3. Run the server

From the monorepo root:

```bash
uv run --project apps/api uvicorn src.main:app --reload --port 8000
```

On first startup the API will automatically create all database tables.

## 4. Run migrations (optional)

If you need to run Alembic migrations explicitly:

```bash
cd apps/api
uv run alembic upgrade head
```

## 5. Access

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
