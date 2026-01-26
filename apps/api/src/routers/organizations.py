"""Organization management routes."""

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db.models import Agent, Organization

router = APIRouter()


class OrganizationCreate(BaseModel):
    """Request model for creating an organization."""

    name: str
    time_zone: str = "UTC"
    country: str | None = None
    currency: str = "USD"


class OrganizationResponse(BaseModel):
    """Response model for organization."""

    id: str
    name: str
    slug: str
    time_zone: str
    country: str | None
    currency: str
    created_at: int

    class Config:
        from_attributes = True


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """Create a new organization with a default agent."""
    # Generate unique slug
    base_slug = generate_slug(data.name)
    slug = base_slug

    # Check if slug exists and make unique if needed
    counter = 1
    while True:
        result = await db.execute(select(Organization).where(Organization.slug == slug))
        if result.scalar_one_or_none() is None:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create organization
    org = Organization(
        name=data.name,
        slug=slug,
        time_zone=data.time_zone,
        country=data.country,
        currency=data.currency,
    )
    db.add(org)
    await db.flush()

    # Create default agent for the organization
    agent = Agent(
        org_id=org.id,
        name="Majster",
        prompt="",  # Empty prompt - will be generated dynamically
        is_custom_prompt=False,
    )
    db.add(agent)

    return org


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
) -> list[Organization]:
    """List all organizations."""
    result = await db.execute(
        select(Organization).where(Organization.deleted_at.is_(None)).order_by(Organization.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """Get a specific organization."""
    result = await db.execute(
        select(Organization).where(
            Organization.id == org_id,
            Organization.deleted_at.is_(None),
        )
    )
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
