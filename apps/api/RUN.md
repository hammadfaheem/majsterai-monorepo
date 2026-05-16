# Running the API

The project uses **uv** for dependency management. Run all commands from the monorepo root (`monorepo/`) unless otherwise noted.

## 1. Install dependencies

```bash
uv sync
```

## 2. Configure environment

Copy the example file and fill in your values:

```bash
cp apps/api/.env.example apps/api/.env
```

Key variables to set:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon (or any PostgreSQL) connection string |
| `JWT_SECRET` | Random secret — generate with `openssl rand -hex 32` |
| `LIVEKIT_URL` | Your LiveKit Cloud project WebSocket URL |
| `LIVEKIT_API_KEY` | LiveKit API key |
| `LIVEKIT_API_SECRET` | LiveKit API secret |

Optional (phone/SIP features — leave unset to disable):

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `BASE_URL` | Public API URL for Twilio webhook callbacks |

> **Neon tip:** Copy the connection string from your [Neon Console](https://console.neon.tech) → project → **Connection string**.
> The `channel_binding=require` parameter is automatically stripped at runtime — you can leave it in the URL as-is.

## 3. Run database migrations

Schema is managed exclusively by Alembic. Run once before starting the server and again after every schema change:

```bash
uv run --project apps/api alembic upgrade head
```

## 4. Start the server

```bash
uv run --project apps/api uvicorn src.main:app --reload --port 8000
```

## 5. Access

- API docs: http://localhost:8000/docs  *(only available when `DEBUG=true`)*
- Health check: http://localhost:8000/health
