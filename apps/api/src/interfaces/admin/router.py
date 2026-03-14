"""Admin (superadmin) routes – list/update organizations and users."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.organization.get_organization import GetOrganizationUseCase
from ...application.organization.list_organizations import ListOrganizationsUseCase
from ...application.organization.update_organization import UpdateOrganizationUseCase
from ...db.database import get_db
from ...domain.user.entity import User as UserEntity
from ...infrastructure.database.repositories import (
    OrganizationRepository,
    SQLAlchemyOrganizationRepository,
    SQLAlchemyUserRepository,
    UserRepository,
)
from ...shared.exceptions import NotFoundError
from ..auth.router import require_superadmin
from ..organization.router import OrganizationResponse, OrganizationUpdate

router = APIRouter()


def get_org_repo(db: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    return SQLAlchemyOrganizationRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db)


# --- Users (admin-only) ---
class AdminUserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str | None
    created_at: int

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    role: str | None = None


# --- Organizations (admin-only) ---
@router.get("/organizations", response_model=list[OrganizationResponse])
async def admin_list_organizations(
    _: UserEntity = Depends(require_superadmin),
    org_repo: OrganizationRepository = Depends(get_org_repo),
):
    """List all organizations (superadmin only)."""
    use_case = ListOrganizationsUseCase(org_repo)
    orgs = await use_case.execute()
    return [
        OrganizationResponse(
            id=o.id,
            name=o.name,
            slug=o.slug,
            time_zone=o.time_zone,
            country=o.country,
            currency=o.currency,
            created_at=o.created_at,
            stripe_plan=o.stripe_plan,
            stripe_customer_id=o.stripe_customer_id,
            default_schedule_id=o.default_schedule_id,
            public_scheduler_configurations=o.public_scheduler_configurations,
            tag=o.tag,
            seats=o.seats,
            addons=o.addons,
        )
        for o in orgs
    ]


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def admin_get_organization(
    org_id: str,
    _: UserEntity = Depends(require_superadmin),
    org_repo: OrganizationRepository = Depends(get_org_repo),
):
    """Get one organization (superadmin only)."""
    use_case = GetOrganizationUseCase(org_repo)
    try:
        o = await use_case.execute(org_id)
        return OrganizationResponse(
            id=o.id,
            name=o.name,
            slug=o.slug,
            time_zone=o.time_zone,
            country=o.country,
            currency=o.currency,
            created_at=o.created_at,
            stripe_plan=o.stripe_plan,
            stripe_customer_id=o.stripe_customer_id,
            default_schedule_id=o.default_schedule_id,
            public_scheduler_configurations=o.public_scheduler_configurations,
            tag=o.tag,
            seats=o.seats,
            addons=o.addons,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
async def admin_update_organization(
    org_id: str,
    data: OrganizationUpdate,
    _: UserEntity = Depends(require_superadmin),
    org_repo: OrganizationRepository = Depends(get_org_repo),
):
    """Update any organization (superadmin only)."""
    use_case = UpdateOrganizationUseCase(org_repo)
    try:
        o = await use_case.execute(
            org_id,
            name=data.name,
            time_zone=data.time_zone,
            country=data.country,
            currency=data.currency,
            stripe_plan=data.stripe_plan,
            stripe_customer_id=data.stripe_customer_id,
            default_schedule_id=data.default_schedule_id,
            public_scheduler_configurations=data.public_scheduler_configurations,
            tag=data.tag,
            seats=data.seats,
            addons=data.addons,
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    return OrganizationResponse(
        id=o.id,
        name=o.name,
        slug=o.slug,
        time_zone=o.time_zone,
        country=o.country,
        currency=o.currency,
        created_at=o.created_at,
        stripe_plan=o.stripe_plan,
        stripe_customer_id=o.stripe_customer_id,
        default_schedule_id=o.default_schedule_id,
        public_scheduler_configurations=o.public_scheduler_configurations,
        tag=o.tag,
        seats=o.seats,
        addons=o.addons,
    )


# --- Users (admin-only) ---
@router.get("/users", response_model=list[AdminUserResponse])
async def admin_list_users(
    _: UserEntity = Depends(require_superadmin),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """List all users (superadmin only)."""
    users = await user_repo.list_all()
    return [
        AdminUserResponse(id=u.id, email=u.email, name=u.name, role=u.role, created_at=u.created_at)
        for u in users
    ]


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def admin_get_user(
    user_id: str,
    _: UserEntity = Depends(require_superadmin),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """Get one user (superadmin only)."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
    )


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def admin_update_user(
    user_id: str,
    data: AdminUserUpdate,
    _: UserEntity = Depends(require_superadmin),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """Update user platform role (superadmin only)."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.role is not None:
        user.role = data.role
    updated = await user_repo.update(user)
    return AdminUserResponse(
        id=updated.id,
        email=updated.email,
        name=updated.name,
        role=updated.role,
        created_at=updated.created_at,
    )
