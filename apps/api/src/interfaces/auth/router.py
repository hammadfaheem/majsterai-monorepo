"""Authentication routes."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.auth.register_with_org import RegisterWithOrgUseCase
from ...application.user.authenticate_user import AuthenticateUserUseCase
from ...application.user.get_user import GetUserUseCase
from ...config import get_settings
from ...db.database import get_db
from ...domain.user.entity import User as UserEntity
from ...infrastructure.database.repositories import (
    AgentRepository,
    MembershipRepository,
    OrganizationRepository,
    SQLAlchemyAgentRepository,
    SQLAlchemyMembershipRepository,
    SQLAlchemyOrganizationRepository,
    SQLAlchemyUserRepository,
    UserRepository,
)

router = APIRouter()

JWT_ALGORITHM = "HS256"


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency to get user repository."""
    return SQLAlchemyUserRepository(db)


def get_org_repo(db: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    """Dependency to get organization repository."""
    return SQLAlchemyOrganizationRepository(db)


def get_agent_repo(db: AsyncSession = Depends(get_db)) -> AgentRepository:
    """Dependency to get agent repository."""
    return SQLAlchemyAgentRepository(db)


def get_membership_repo(db: AsyncSession = Depends(get_db)) -> MembershipRepository:
    """Dependency to get membership repository."""
    return SQLAlchemyMembershipRepository(db)


class UserRegister(BaseModel):
    """Request model for user registration."""

    email: str
    name: str
    password: str
    # Optional onboarding data (from /onboarding flow)
    org_name: str | None = None
    time_zone: str | None = None
    country: str | None = None
    currency: str | None = None


class UserLogin(BaseModel):
    """Request model for user login."""

    email: str
    password: str


class UserResponse(BaseModel):
    """Response model for user."""

    id: str
    email: str
    name: str
    created_at: int
    role: str | None = None

    class Config:
        from_attributes = True


async def get_current_user_dep(
    authorization: str | None = Header(None, alias="Authorization"),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserEntity:
    """Dependency: resolve JWT and return current user entity or raise 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.replace("Bearer ", "")
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    use_case = GetUserUseCase(user_repo)
    user = await use_case.execute(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def require_superadmin(
    current_user: UserEntity = Depends(get_current_user_dep),
) -> UserEntity:
    """Dependency: require current user to be SUPERADMIN or raise 403."""
    if current_user.role != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Forbidden: superadmin required")
    return current_user


class AuthResponse(BaseModel):
    """Response model for authentication."""

    access_token: str
    user: UserResponse


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    settings = get_settings()
    expiration = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    payload = {"sub": user_id, "exp": expiration}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


@router.post("/register", response_model=AuthResponse)
async def register(
    data: UserRegister,
    user_repo: UserRepository = Depends(get_user_repo),
    org_repo: OrganizationRepository = Depends(get_org_repo),
    agent_repo: AgentRepository = Depends(get_agent_repo),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    """Register a new user with default organization and agent."""
    use_case = RegisterWithOrgUseCase(
        user_repo=user_repo,
        org_repo=org_repo,
        agent_repo=agent_repo,
        membership_repo=membership_repo,
    )
    try:
        user = await use_case.execute(
            data.email,
            data.name,
            data.password,
            org_name=data.org_name,
            time_zone=data.time_zone or "UTC",
            country=data.country,
            currency=data.currency or "USD",
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    access_token = create_access_token(user.id)
    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            role=user.role,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLogin,
    user_repo: UserRepository = Depends(get_user_repo),
):
    """Login user."""
    use_case = AuthenticateUserUseCase(user_repo)
    user = await use_case.execute(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(user.id)
    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserEntity = Depends(get_current_user_dep)):
    """Get current user from JWT token."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        role=current_user.role,
    )


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)."""
    return {"message": "Logged out successfully"}
