"""Organization management routes - Clean Architecture."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.organization.create_organization import CreateOrganizationUseCase
from ...application.organization.get_organization import GetOrganizationUseCase
from ...application.organization.list_organizations import ListOrganizationsUseCase
from ...application.organization.update_organization import UpdateOrganizationUseCase
from ...db.database import get_db
from ...infrastructure.database.repositories import (
    AgentRepository,
    OrganizationRepository,
    SQLAlchemyAgentRepository,
    SQLAlchemyOrganizationRepository,
)
from ...shared.exceptions import NotFoundError
from ..auth.router import get_current_user_dep
from ...domain.user.entity import User as UserEntity

router = APIRouter()


class OrganizationCreate(BaseModel):
    """Request model for creating an organization."""

    name: str
    time_zone: str = "UTC"
    country: str | None = None
    currency: str = "USD"


class OrganizationUpdate(BaseModel):
    """Request model for updating an organization (partial)."""

    name: str | None = None
    time_zone: str | None = None
    country: str | None = None
    currency: str | None = None
    settings: dict | None = None
    stripe_plan: str | None = None
    stripe_customer_id: str | None = None
    default_schedule_id: int | None = None
    public_scheduler_configurations: dict | None = None
    tag: str | None = None
    seats: int | None = None
    addons: dict | None = None


class OrganizationResponse(BaseModel):
    """Response model for organization."""

    id: str
    name: str
    slug: str
    time_zone: str
    country: str | None
    currency: str
    settings: dict | None = None
    created_at: int
    stripe_plan: str | None = None
    stripe_customer_id: str | None = None
    default_schedule_id: int | None = None
    public_scheduler_configurations: dict | None = None
    tag: str | None = None
    seats: int | None = None
    addons: dict | None = None

    class Config:
        from_attributes = True


def get_org_repo(db: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    """Dependency to get organization repository."""
    return SQLAlchemyOrganizationRepository(db)


def get_agent_repo(db: AsyncSession = Depends(get_db)) -> AgentRepository:
    """Dependency to get agent repository."""
    return SQLAlchemyAgentRepository(db)


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    data: OrganizationCreate,
    org_repo: OrganizationRepository = Depends(get_org_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
):
    """Create a new organization with a default agent."""
    use_case = CreateOrganizationUseCase(org_repo, agent_repo)
    try:
        organization, _ = await use_case.execute(
            name=data.name,
            time_zone=data.time_zone,
            country=data.country,
            currency=data.currency,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        time_zone=organization.time_zone,
        country=organization.country,
        currency=organization.currency,
        settings=organization.settings,
        created_at=organization.created_at,
        stripe_plan=organization.stripe_plan,
        stripe_customer_id=organization.stripe_customer_id,
        default_schedule_id=organization.default_schedule_id,
        public_scheduler_configurations=organization.public_scheduler_configurations,
        tag=organization.tag,
        seats=organization.seats,
        addons=organization.addons,
    )


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    data: OrganizationUpdate,
    org_repo: OrganizationRepository = Depends(get_org_repo),
):
    """Update an organization (partial update)."""
    use_case = UpdateOrganizationUseCase(org_repo)
    try:
        organization = await use_case.execute(
            org_id,
            name=data.name,
            time_zone=data.time_zone,
            country=data.country,
            currency=data.currency,
            settings=data.settings,
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
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        time_zone=organization.time_zone,
        country=organization.country,
        currency=organization.currency,
        settings=organization.settings,
        created_at=organization.created_at,
        stripe_plan=organization.stripe_plan,
        stripe_customer_id=organization.stripe_customer_id,
        default_schedule_id=organization.default_schedule_id,
        public_scheduler_configurations=organization.public_scheduler_configurations,
        tag=organization.tag,
        seats=organization.seats,
        addons=organization.addons,
    )


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    current_user: UserEntity = Depends(get_current_user_dep),
    org_repo: OrganizationRepository = Depends(get_org_repo),
):
    """List organizations (all for SUPERADMIN, else only orgs where current user is member)."""
    use_case = ListOrganizationsUseCase(org_repo)
    organizations = await use_case.execute(user_id=current_user.id, user_role=current_user.role)
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            time_zone=org.time_zone,
            country=org.country,
            currency=org.currency,
            settings=org.settings,
            created_at=org.created_at,
            stripe_plan=org.stripe_plan,
            stripe_customer_id=org.stripe_customer_id,
            default_schedule_id=org.default_schedule_id,
            public_scheduler_configurations=org.public_scheduler_configurations,
            tag=org.tag,
            seats=org.seats,
            addons=org.addons,
        )
        for org in organizations
    ]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    org_repo: OrganizationRepository = Depends(get_org_repo),
):
    """Get a specific organization."""
    use_case = GetOrganizationUseCase(org_repo)
    try:
        organization = await use_case.execute(org_id)
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            time_zone=organization.time_zone,
            country=organization.country,
            currency=organization.currency,
            settings=organization.settings,
            created_at=organization.created_at,
            stripe_plan=organization.stripe_plan,
            stripe_customer_id=organization.stripe_customer_id,
            default_schedule_id=organization.default_schedule_id,
            public_scheduler_configurations=organization.public_scheduler_configurations,
            tag=organization.tag,
            seats=organization.seats,
            addons=organization.addons,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
