# MajsterAI Monorepo

Voice AI Agent Platform - Build, test, and deploy intelligent voice assistants.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  User Browser                                                   │
│  (Next.js Dashboard)                                            │
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
│   │   └── dashboard/        # Next.js frontend
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
- Docker (for PostgreSQL)

### 0. Clone the Repository

```bash
git clone git@github.com:hammadfaheem/majsterai-monorepo.git
cd majsterai-monorepo
```

### 1. Start Database

```bash
# Copy .env.example to .env and update with your values
cp .env.example .env
# Edit .env with your PostgreSQL credentials
docker compose up -d postgres
```

### 2. Setup FastAPI Backend

```bash
cd apps/api
uv sync
cp .env.example .env  # Edit with your credentials
# Edit .env with your LiveKit and database credentials
uv run uvicorn src.main:app --reload --port 8000
```

### 3. Setup Dashboard

```bash
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

1. Open http://localhost:3000
2. Create an organization
3. Click "Test Agent"
4. Start talking!

## Environment Variables

### Root Directory (.env)
For Docker Compose services (PostgreSQL, Redis):

```env
# PostgreSQL
POSTGRES_USER=majsterai
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=majsterai
```

### API Directory (apps/api/.env)
For the FastAPI backend:

```env
# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Database
DATABASE_URL=postgresql://majsterai:your_password_here@localhost:5432/majsterai

# Application
ENVIRONMENT=development
DEBUG=true

# AI Models (optional)
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
```

**Important:** Never commit `.env` files to git. Always use `.env.example` as a template.

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

```bash
cd apps/api
uv run uvicorn src.main:app --reload
uv run pytest  # Run tests
uv run ruff check .  # Lint
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
