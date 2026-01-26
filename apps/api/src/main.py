"""MajsterAI API - Main FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db.database import init_db
from .routers import agents, livekit, organizations

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="MajsterAI API",
    description="Voice AI Agent Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(organizations.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(livekit.router, prefix="/api/livekit", tags=["livekit"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MajsterAI API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
