"""Create user use case."""

import bcrypt
from ...db.database import generate_uuid, utc_now_ms
from ...domain.user.entity import User
from ...infrastructure.database.repositories import UserRepository


class CreateUserUseCase:
    """Use case for creating a new user."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str, name: str, password: str) -> User:
        """Create a new user."""
        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Create user entity
        user = User(
            id=generate_uuid(),
            email=email,
            name=name,
            password_hash=password_hash,
            created_at=utc_now_ms(),
            updated_at=utc_now_ms(),
            deleted_at=None,
        )

        # Save to repository
        return await self.user_repo.create(user)
