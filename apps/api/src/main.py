"""MajsterAI API - Main FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import get_settings
from .db.database import async_session_maker, init_db, ping_db
from .infrastructure.database.repositories import SQLAlchemyUserRepository
from .shared.exceptions import AppException, ConflictError, NotFoundError, ValidationError
from .shared.middleware import LoggingMiddleware, RequestIDMiddleware
from .interfaces.admin.router import router as admin_router
from .interfaces.calendar.router import router as calendar_router
from .interfaces.agent.router import router as agents_router
from .interfaces.appointment.router import router as appointment_router
from .interfaces.auth.router import router as auth_router
from .interfaces.availability.router import router as availability_router
from .interfaces.call_history.router import router as call_history_router
from .interfaces.department.router import router as department_router
from .interfaces.invoice.router import router as invoice_router
from .interfaces.lead.router import router as lead_router
from .interfaces.lead_address.router import router as lead_address_router
from .interfaces.livekit.router import router as livekit_router
from .interfaces.membership.router import router as membership_router
from .interfaces.membership_unavailability.router import (
    router as membership_unavailability_router,
)
from .interfaces.notification_log.router import router as notification_log_router
from .interfaces.notification_type.router import router as notification_type_router
from .interfaces.org_notification_recipient.router import (
    router as org_notification_recipient_router,
)
from .interfaces.organization.router import router as organizations_router
from .interfaces.reminder.router import router as reminder_router
from .interfaces.scenario.router import router as scenario_router
from .interfaces.schedule.router import router as schedule_router
from .interfaces.tag_base.router import router as tag_base_router
from .interfaces.task.router import router as task_router
from .interfaces.trade_category.router import router as trade_category_router
from .interfaces.trade_service.router import router as trade_service_router
from .interfaces.transfer.router import router as transfer_router
from .interfaces.twilio.router import router as twilio_router

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------


async def _ensure_superadmin() -> None:
    """If SUPERADMIN_EMAIL is set, grant that user SUPERADMIN role on startup."""
    email = settings.superadmin_email
    if not email or not email.strip():
        return
    async with async_session_maker() as session:
        try:
            repo = SQLAlchemyUserRepository(session)
            user = await repo.get_by_email(email.strip())
            if user and user.role != "SUPERADMIN":
                user.role = "SUPERADMIN"
                await repo.update(user)
                await session.commit()
        except Exception:
            logger.exception("Failed to ensure superadmin role for %s", email.strip())
            await session.rollback()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan — verify DB connectivity on startup."""
    await init_db()
    await _ensure_superadmin()
    yield


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="MajsterAI API",
    description="Voice AI Agent Platform API",
    version="0.1.0",
    lifespan=lifespan,
    # Hide /docs and /redoc in production
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Middleware — order matters: added last executes first
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict to the explicit method/header set the API actually uses
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


# ---------------------------------------------------------------------------
# Global exception handlers — map domain errors to HTTP responses centrally
# so individual routers never need to re-catch them.
# ---------------------------------------------------------------------------


@app.exception_handler(NotFoundError)
async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc) or "Resource not found"})


@app.exception_handler(ConflictError)
async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc) or "Resource conflict"})


@app.exception_handler(ValidationError)
async def validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc) or "Validation error"})


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    logger.exception("Unhandled application error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred"})


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(organizations_router, prefix="/api/organizations", tags=["organizations"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(livekit_router, prefix="/api/livekit", tags=["livekit"])
app.include_router(membership_router, prefix="/api/memberships", tags=["memberships"])
app.include_router(
    membership_unavailability_router,
    prefix="/api/membership-unavailability",
    tags=["membership-unavailability"],
)
app.include_router(lead_router, prefix="/api/leads", tags=["leads"])
app.include_router(call_history_router, prefix="/api/call-history", tags=["call-history"])
app.include_router(schedule_router, prefix="/api/schedules", tags=["schedules"])
app.include_router(department_router, prefix="/api/departments", tags=["departments"])
app.include_router(appointment_router, prefix="/api/appointments", tags=["appointments"])
app.include_router(
    trade_category_router, prefix="/api/trade-categories", tags=["trade-categories"]
)
app.include_router(
    trade_service_router, prefix="/api/trade-services", tags=["trade-services"]
)
app.include_router(invoice_router, prefix="/api/invoices", tags=["invoices"])
app.include_router(scenario_router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(tag_base_router, prefix="/api/tag-bases", tags=["tag-bases"])
app.include_router(task_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(transfer_router, prefix="/api/transfers", tags=["transfers"])
app.include_router(reminder_router, prefix="/api/reminders", tags=["reminders"])
app.include_router(lead_address_router, prefix="/api/lead-addresses", tags=["lead-addresses"])
app.include_router(availability_router, prefix="/api/availabilities", tags=["availabilities"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(twilio_router, prefix="/api/twilio", tags=["twilio"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(
    notification_type_router, prefix="/api/notification-types", tags=["notification-types"]
)
app.include_router(
    notification_log_router, prefix="/api/notification-logs", tags=["notification-logs"]
)
app.include_router(
    org_notification_recipient_router,
    prefix="/api/org-notification-recipients",
    tags=["org-notification-recipients"],
)


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"message": "MajsterAI API", "version": "0.1.0"}


@app.get("/health", tags=["system"])
async def health() -> JSONResponse:
    """Liveness + readiness probe.

    Returns 200 when the database is reachable, 503 otherwise.
    Load balancers and Kubernetes readinessProbe should use this endpoint.
    """
    db_ok = await ping_db()
    status = "healthy" if db_ok else "unhealthy"
    code = 200 if db_ok else 503
    return JSONResponse(
        status_code=code,
        content={
            "status": status,
            "database": "ok" if db_ok else "unreachable",
        },
    )
