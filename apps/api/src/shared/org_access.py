"""Organization access control – require current user to be org member or SUPERADMIN."""

from fastapi import Depends, HTTPException

from ..domain.user.entity import User as UserEntity
from ..interfaces.auth.router import get_current_user_dep, get_membership_repo
from ..infrastructure.database.repositories import MembershipRepository


async def verify_org_access(
    org_id: str,
    current_user: UserEntity,
    membership_repo: MembershipRepository,
) -> None:
    """Verify user has access to org (member or SUPERADMIN). Raises 403 if not."""
    if current_user.role == "SUPERADMIN":
        return
    membership = await membership_repo.get_by_org_and_user(org_id, current_user.id)
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Not a member of this organization",
        )


async def require_org_membership(
    org_id: str,
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
) -> None:
    """Dependency: require current user to be a member of the organization or SUPERADMIN.

    Use with routes that have org_id in the path, e.g. @router.get("/org/{org_id}").
    Raises 403 if user is not a member.
    """
    await verify_org_access(org_id, current_user, membership_repo)
