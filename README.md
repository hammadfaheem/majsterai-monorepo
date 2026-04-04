# MajsterAI Monorepo

Voice AI Agent Platform - Build, test, and deploy intelligent voice assistants.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  User Browser                                                   │
│  (Vite + React Dashboard)                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Backend (apps/api)                                     │
│  - Organization management                                      │
│  - Agent configuration                                          │
│  - LiveKit room creation with metadata                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│  PostgreSQL          │    │  LiveKit Cloud       │
│  (Organizations,     │    │  (WebRTC, Voice)     │
│   Agents, Calls)     │    │                      │
└──────────────────────┘    └──────────┬───────────┘
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │  MajsterAI Agent     │
                            │  (majsterai-agent/)  │
                            │  Reads prompt from   │
                            │  room metadata       │
                            └──────────────────────┘
```

## Structure

```
majsterai/
├── monorepo/                 # This directory
│   ├── apps/
│   │   ├── api/              # FastAPI backend (Python)
│   │   └── dashboard/        # Vite + React frontend (TypeScript)
│   ├── packages/             # Shared packages (future)
│   └── internal/             # Internal libraries (future)
│
└── majsterai-agent/          # LiveKit Voice Agent (separate)
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- pnpm 9+
- uv (Python package manager)
- A [Neon](https://neon.tech) account (serverless PostgreSQL — no local Docker needed)

### 0. Clone the Repository

```bash
git clone git@github.com:hammadfaheem/majsterai-monorepo.git
cd majsterai-monorepo
```

### 1. Configure the API environment

Create `apps/api/.env` with your Neon connection string and LiveKit credentials:

```bash
cp apps/api/.env.example apps/api/.env  # if example exists, otherwise create it
# Edit apps/api/.env with your Neon DATABASE_URL and LiveKit keys
```

### 2. Setup and run the FastAPI Backend

From the monorepo root:

```bash
uv sync
uv run --project apps/api uvicorn src.main:app --reload --port 8000
```

Run migrations on first startup (and after each deployment):

```bash
uv run --project apps/api alembic upgrade head
```

### 3. Configure and run the Dashboard

```bash
cp apps/dashboard/.env.example apps/dashboard/.env
# Edit apps/dashboard/.env if your API runs on a different URL
cd apps/dashboard
pnpm install
pnpm dev
```

### 4. Start the Agent (separate terminal)

```bash
# Clone the agent repository (if not already cloned)
git clone git@github.com:hammadfaheem/majsterai-agent.git majsterai-agent
cd majsterai-agent
uv sync
# Edit .env with LiveKit credentials
uv run python -m livekit.agents dev src/main.py dev
```

### 5. Test

1. Open http://localhost:5173
2. Create an organization
3. Click "Test Agent"
4. Start talking!

## Environment Variables

### API Directory (`apps/api/.env`)

```env
# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# Application
ENVIRONMENT=development
DEBUG=true
```

Get your `DATABASE_URL` from the [Neon Console](https://console.neon.tech) → your project → **Connection string**.
The `sslmode=require` and `channel_binding` parameters are handled automatically.

**Important:** Never commit `.env` files to git.

## API Endpoints

### Organizations

- `POST /api/organizations/` - Create organization
- `GET /api/organizations/` - List organizations
- `GET /api/organizations/{id}` - Get organization

### Agents

- `GET /api/agents/{org_id}` - Get agent config
- `PUT /api/agents/{org_id}` - Update agent config

### LiveKit

- `POST /api/livekit/create-room` - Create room with agent config
- `POST /api/livekit/token` - Generate participant token

## How It Works

1. **Organization creates agent config** → Stored in PostgreSQL
2. **User clicks "Test Agent"** → Dashboard calls FastAPI
3. **FastAPI creates LiveKit room** → Includes agent config in room metadata
4. **Agent receives job dispatch** → Reads metadata from `ctx.room.metadata`
5. **Agent uses dynamic prompt** → No redeployment needed for prompt changes

This pattern (from SOFi architecture) enables:
- Multi-tenant support (different prompts per org)
- Real-time prompt updates
- Centralized configuration management

## Development

### FastAPI Backend

From the monorepo root:

```bash
uv run --project apps/api uvicorn src.main:app --reload --port 8000
uv run --project apps/api pytest          # Run tests
uv run --project apps/api ruff check src  # Lint
```

### Dashboard

```bash
cd apps/dashboard
pnpm dev
pnpm build
pnpm lint
```

### Agent

```bash
# Clone the agent repository (if not already cloned)
git clone git@github.com:hammadfaheem/majsterai-agent.git majsterai-agent
cd majsterai-agent
uv sync
# Edit .env with LiveKit credentials
uv run python -m livekit.agents dev src/main.py dev
```

## License

Proprietary - MajsterAI
