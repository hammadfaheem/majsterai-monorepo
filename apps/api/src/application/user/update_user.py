"""Update user use case."""

from ...db.database import utc_now_ms
from ...domain.user.entity import User
from ...infrastructure.database.repositories import UserRepository
from ...shared.exceptions import NotFoundError


class UpdateUserUseCase:
    """Use case for updating a user."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(
        self, user_id: str, name: str | None = None, email: str | None = None
    ) -> User:
        """Update user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email

        user.updated_at = utc_now_ms()

        return await self.user_repo.update(user)
