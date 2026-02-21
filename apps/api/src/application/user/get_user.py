"""Get user use case."""

from ...domain.user.entity import User
from ...infrastructure.database.repositories import UserRepository


class GetUserUseCase:
    """Use case for getting a user."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: str) -> User | None:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)
