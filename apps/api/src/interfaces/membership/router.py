"""Membership management routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.membership.add_member import AddMemberUseCase
from ...application.membership.list_members import ListMembersUseCase
from ...application.membership.remove_member import RemoveMemberUseCase
from ...application.membership.update_member_role import UpdateMemberRoleUseCase
from ...db.database import get_db
from ...infrastructure.database.repositories import (
    MembershipRepository,
    SQLAlchemyMembershipRepository,
    SQLAlchemyUserRepository,
    UserRepository,
)
from ...shared.exceptions import NotFoundError

router = APIRouter()


def get_membership_repo(db: AsyncSession = Depends(get_db)) -> MembershipRepository:
    """Dependency to get membership repository."""
    return SQLAlchemyMembershipRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency to get user repository."""
    return SQLAlchemyUserRepository(db)


class MembershipResponse(BaseModel):
    """Response model for membership."""

    id: str
    org_id: str
    user_id: str | None
    role: str
    created_at: int
    updated_at: int
    invited_email: str | None = None
    is_disabled: bool = False
    is_point_of_escalation: bool = False
    scheduling_priority: int | None = None
    responsibility: str | None = None
    personalisation_notes: str | None = None

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    """Request model for adding a member."""

    user_id: str
    role: str = "member"
    invited_email: str | None = None
    scheduling_priority: int | None = None
    responsibility: str | None = None
    personalisation_notes: str | None = None
    is_point_of_escalation: bool = False


class UpdateMemberRoleRequest(BaseModel):
    """Request model for updating member role."""

    role: str | None = None
    is_disabled: bool | None = None
    is_point_of_escalation: bool | None = None
    scheduling_priority: int | None = None
    responsibility: str | None = None
    personalisation_notes: str | None = None


@router.get("/{org_id}", response_model=list[MembershipResponse])
async def list_members(
    org_id: str,
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    """List all members of an organization."""
    use_case = ListMembersUseCase(membership_repo)
    memberships = await use_case.execute(org_id)
    return [
        MembershipResponse(
            id=m.id,
            org_id=m.org_id,
            user_id=m.user_id,
            role=m.role,
            created_at=m.created_at,
            updated_at=m.updated_at,
            invited_email=m.invited_email,
            is_disabled=m.is_disabled,
            is_point_of_escalation=m.is_point_of_escalation,
            scheduling_priority=m.scheduling_priority,
            responsibility=m.responsibility,
            personalisation_notes=m.personalisation_notes,
        )
        for m in memberships
    ]


@router.post("/{org_id}", response_model=MembershipResponse)
async def add_member(
    org_id: str,
    data: AddMemberRequest,
    membership_repo: MembershipRepository = Depends(get_membership_repo),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """Add a member to an organization."""
    use_case = AddMemberUseCase(membership_repo, user_repo)
    try:
        membership = await use_case.execute(
            org_id,
            data.user_id,
            data.role,
            invited_email=data.invited_email,
            scheduling_priority=data.scheduling_priority,
            responsibility=data.responsibility,
            personalisation_notes=data.personalisation_notes,
            is_point_of_escalation=data.is_point_of_escalation,
        )
        return MembershipResponse(
            id=membership.id,
            org_id=membership.org_id,
            user_id=membership.user_id,
            role=membership.role,
            created_at=membership.created_at,
            updated_at=membership.updated_at,
            invited_email=membership.invited_email,
            is_disabled=membership.is_disabled,
            is_point_of_escalation=membership.is_point_of_escalation,
            scheduling_priority=membership.scheduling_priority,
            responsibility=membership.responsibility,
            personalisation_notes=membership.personalisation_notes,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{org_id}/{user_id}", response_model=MembershipResponse)
async def update_member_role(
    org_id: str,
    user_id: str,
    data: UpdateMemberRoleRequest,
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    """Update a member's role and profile."""
    use_case = UpdateMemberRoleUseCase(membership_repo)
    try:
        membership = await use_case.execute(
            org_id,
            user_id,
            role=data.role,
            is_disabled=data.is_disabled,
            is_point_of_escalation=data.is_point_of_escalation,
            scheduling_priority=data.scheduling_priority,
            responsibility=data.responsibility,
            personalisation_notes=data.personalisation_notes,
        )
        return MembershipResponse(
            id=membership.id,
            org_id=membership.org_id,
            user_id=membership.user_id,
            role=membership.role,
            created_at=membership.created_at,
            updated_at=membership.updated_at,
            invited_email=membership.invited_email,
            is_disabled=membership.is_disabled,
            is_point_of_escalation=membership.is_point_of_escalation,
            scheduling_priority=membership.scheduling_priority,
            responsibility=membership.responsibility,
            personalisation_notes=membership.personalisation_notes,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{org_id}/{user_id}")
async def remove_member(
    org_id: str,
    user_id: str,
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    """Remove a member from an organization."""
    use_case = RemoveMemberUseCase(membership_repo)
    try:
        await use_case.execute(org_id, user_id)
        return {"message": "Member removed successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
