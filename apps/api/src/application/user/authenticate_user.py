"""Authenticate user use case."""

import bcrypt
from ...domain.user.entity import User
from ...infrastructure.database.repositories import UserRepository


class AuthenticateUserUseCase:
    """Use case for authenticating a user."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None

        # Verify password
        if bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return user

        return None
