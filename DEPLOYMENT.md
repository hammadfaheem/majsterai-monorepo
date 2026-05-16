# MajsterAI Deployment Guide

Three independent pieces to deploy:

| Component | What it is | Where it runs |
|-----------|-----------|---------------|
| **API** | FastAPI backend | VPS / cloud VM |
| **Dashboard** | Vite + React SPA | Nginx (same VPS) or static host |
| **Agent** | LiveKit voice agent | LiveKit Cloud (managed) |

The **database** (Neon) is already cloud-hosted — nothing to deploy there.

---

## Prerequisites

On your server (Ubuntu 22.04+ recommended):

```bash
# Python + uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node + pnpm
curl -fsSL https://fnm.vercel.app/install | bash
fnm install 20
npm install -g pnpm@9

# Nginx + Certbot
sudo apt install -y nginx certbot python3-certbot-nginx git
```

On your local machine:

```bash
# LiveKit CLI (for agent deployment)
curl -sSL https://get.livekit.io/cli | bash
```

---

## Part 1 — API (FastAPI)

### 1.1 Clone and install

```bash
git clone git@github.com:hammadfaheem/majsterai-monorepo.git /opt/majsterai
cd /opt/majsterai
uv sync
```

### 1.2 Configure environment

```bash
cp apps/api/.env.example apps/api/.env
nano apps/api/.env
```

Required values for production:

```env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET=<openssl rand -hex 32>
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
CORS_ORIGINS=https://your-dashboard-domain.com
BASE_URL=https://your-api-domain.com
```

> The API will **refuse to start** in `production` mode if `DEBUG=true` or `BASE_URL` is still the placeholder.

### 1.3 Run database migrations

```bash
cd /opt/majsterai
uv run --project apps/api alembic upgrade head
```

Run this again after every deployment that includes schema changes.

### 1.4 Create a systemd service

```bash
sudo nano /etc/systemd/system/majsterai-api.service
```

```ini
[Unit]
Description=MajsterAI FastAPI
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/majsterai
ExecStart=/root/.local/bin/uv run --project apps/api \
    uvicorn src.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 2
Restart=always
RestartSec=5
Environment=PATH=/root/.local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now majsterai-api
sudo systemctl status majsterai-api
```

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"healthy","database":"ok"}
```

### 1.5 Nginx reverse proxy for the API

```bash
sudo nano /etc/nginx/sites-available/majsterai-api
```

```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/majsterai-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Add SSL
sudo certbot --nginx -d api.your-domain.com
```

---

## Part 2 — Dashboard (Vite + React)

### 2.1 Build the frontend

On your server (or in CI):

```bash
cd /opt/majsterai/apps/dashboard
cp .env.example .env.production
```

Edit `.env.production`:

```env
VITE_API_BASE_URL=https://api.your-domain.com
VITE_LIVEKIT_URL=wss://your-project.livekit.cloud
```

```bash
pnpm install
pnpm build
# Output lands in apps/dashboard/dist/
```

### 2.2 Serve with Nginx

```bash
sudo nano /etc/nginx/sites-available/majsterai-dashboard
```

```nginx
server {
    listen 80;
    server_name app.your-domain.com;

    root /opt/majsterai/apps/dashboard/dist;
    index index.html;

    # SPA fallback — all routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets aggressively (Vite hashes filenames)
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/majsterai-dashboard /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Add SSL
sudo certbot --nginx -d app.your-domain.com
```

### 2.3 Redeploying the dashboard

```bash
cd /opt/majsterai
git pull
cd apps/dashboard
pnpm install
pnpm build
# Nginx serves the new dist/ immediately — no restart needed
```

---

## Part 3 — Agent (LiveKit Cloud managed)

The agent runs on LiveKit's infrastructure. You push code; LiveKit builds, deploys, and scales it.

### 3.1 Authenticate the CLI

```bash
lk cloud auth
# Opens browser → log in → links your LiveKit Cloud project
```

### 3.2 Set agent secrets

From the `majsterai-agent/` directory, create a secrets file:

```bash
cd /path/to/majsterai-agent
```

```env
# agent-secrets.env
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
API_BASE_URL=https://api.your-domain.com
DB_ENABLED=true
```

> `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` are **injected automatically** by LiveKit Cloud — do not add them to the secrets file.

### 3.3 Deploy the agent

First deployment:

```bash
lk agent create --secrets-file=agent-secrets.env
```

This:
1. Registers the agent with LiveKit Cloud and creates `livekit.toml`
2. Uploads the code, builds a Docker image from your `Dockerfile`
3. Deploys and starts serving sessions

Monitor progress:

```bash
lk agent status   # replica count, health
lk agent logs     # live log tail
```

### 3.4 Redeploy after code changes

```bash
lk agent deploy
```

LiveKit uses a **rolling deployment** — new sessions go to the new version while existing sessions finish on the old version (up to 1 hour grace period). No downtime.

### 3.5 Update secrets

```bash
lk agent update-secrets --secrets "DATABASE_URL=new-connection-string"
# Triggers a rolling restart automatically
```

### 3.6 Rollback

```bash
lk agent rollback
# Instantly rolls back to the previous build (paid plans)
```

---

## Post-deployment checklist

- [ ] `GET https://api.your-domain.com/health` returns `{"status":"healthy","database":"ok"}`
- [ ] Dashboard loads at `https://app.your-domain.com`
- [ ] Can register/login in the dashboard
- [ ] `lk agent status` shows at least 1 healthy replica
- [ ] Test agent session from the dashboard → agent responds
- [ ] SSL certificates active on both domains (`https://`)
- [ ] `.env` files are **not** committed to git (check `.gitignore`)

---

## Redeployment summary

| What changed | Command |
|-------------|---------|
| API code only | `git pull` → `sudo systemctl restart majsterai-api` |
| DB schema change | `git pull` → `uv run --project apps/api alembic upgrade head` → `sudo systemctl restart majsterai-api` |
| Dashboard code | `git pull` → `cd apps/dashboard && pnpm build` |
| Agent code | `cd majsterai-agent && lk agent deploy` |
| Agent secrets | `lk agent update-secrets --secrets "KEY=value"` |

---

## Keeping the API process alive

The systemd service handles crashes and server reboots automatically. To manage it manually:

```bash
sudo systemctl restart majsterai-api   # restart
sudo systemctl stop majsterai-api      # stop
sudo journalctl -u majsterai-api -f    # live logs
```

---

## Optional: Single-server Nginx config

If both API and dashboard are on the same domain, you can split by path prefix instead of subdomain:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    # Dashboard (SPA)
    root /opt/majsterai/apps/dashboard/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API — proxy /api/* to uvicorn
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

In this setup, set `VITE_API_BASE_URL=` (empty) in the dashboard build — requests to `/api/...` go through the same origin.
