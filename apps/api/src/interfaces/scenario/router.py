"""Scenario routes - CRUD for conversation flows."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...db.database import generate_uuid
from ...domain.scenario.entity import Scenario as ScenarioEntity
from ...domain.user.entity import User as UserEntity
from ...infrastructure.database.repositories import (
    MembershipRepository,
    ScenarioRepository,
    SQLAlchemyScenarioRepository,
)
from ...interfaces.auth.router import get_current_user_dep, get_membership_repo
from ...shared.org_access import require_org_membership, verify_org_access

router = APIRouter()


def get_scenario_repo(db: AsyncSession = Depends(get_db)) -> ScenarioRepository:
    return SQLAlchemyScenarioRepository(db)


class ScenarioCreate(BaseModel):
    org_id: str
    name: str
    prompt: str | None = None
    response: str | None = None
    trigger_type: str | None = None
    trigger_value: str | None = None
    questions: list | None = None
    outcome: dict | None = None
    trade_service_id: int | None = None
    is_active: bool = True


class ScenarioUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None
    response: str | None = None
    trigger_type: str | None = None
    trigger_value: str | None = None
    questions: list | None = None
    outcome: dict | None = None
    trade_service_id: int | None = None
    is_active: bool | None = None


class ScenarioResponse(BaseModel):
    id: str
    org_id: str
    name: str
    prompt: str | None
    response: str | None
    trigger_type: str | None
    trigger_value: str | None
    questions: list | None
    outcome: dict | None
    trade_service_id: int | None
    is_active: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[ScenarioResponse])
async def list_scenarios(
    org_id: str,
    repo: ScenarioRepository = Depends(get_scenario_repo),
):
    items = await repo.list_by_org_id(org_id)
    return [
        ScenarioResponse(
            id=s.id,
            org_id=s.org_id,
            name=s.name,
            prompt=s.prompt,
            response=s.response,
            trigger_type=s.trigger_type,
            trigger_value=s.trigger_value,
            questions=s.questions,
            outcome=s.outcome,
            trade_service_id=s.trade_service_id,
            is_active=s.is_active,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in items
    ]


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: str,
    repo: ScenarioRepository = Depends(get_scenario_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    s = await repo.get_by_id(scenario_id)
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")
    await verify_org_access(s.org_id, current_user, membership_repo)
    return ScenarioResponse(
        id=s.id,
        org_id=s.org_id,
        name=s.name,
        prompt=s.prompt,
        response=s.response,
        trigger_type=s.trigger_type,
        trigger_value=s.trigger_value,
        questions=s.questions,
        outcome=s.outcome,
        trade_service_id=s.trade_service_id,
        is_active=s.is_active,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.post("/", response_model=ScenarioResponse)
async def create_scenario(
    data: ScenarioCreate,
    repo: ScenarioRepository = Depends(get_scenario_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    await verify_org_access(data.org_id, current_user, membership_repo)
    now = utc_now_ms()
    entity = ScenarioEntity(
        id=generate_uuid(),
        org_id=data.org_id,
        name=data.name,
        prompt=data.prompt,
        response=data.response,
        trigger_type=data.trigger_type,
        trigger_value=data.trigger_value,
        questions=data.questions,
        outcome=data.outcome,
        trade_service_id=data.trade_service_id,
        is_active=data.is_active,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return ScenarioResponse(
        id=created.id,
        org_id=created.org_id,
        name=created.name,
        prompt=created.prompt,
        response=created.response,
        trigger_type=created.trigger_type,
        trigger_value=created.trigger_value,
        questions=created.questions,
        outcome=created.outcome,
        trade_service_id=created.trade_service_id,
        is_active=created.is_active,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: str,
    data: ScenarioUpdate,
    repo: ScenarioRepository = Depends(get_scenario_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    existing = await repo.get_by_id(scenario_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Scenario not found")
    await verify_org_access(existing.org_id, current_user, membership_repo)
    now = utc_now_ms()
    if data.name is not None:
        existing.name = data.name
    if data.prompt is not None:
        existing.prompt = data.prompt
    if data.response is not None:
        existing.response = data.response
    if data.trigger_type is not None:
        existing.trigger_type = data.trigger_type
    if data.trigger_value is not None:
        existing.trigger_value = data.trigger_value
    if data.questions is not None:
        existing.questions = data.questions
    if data.outcome is not None:
        existing.outcome = data.outcome
    if data.trade_service_id is not None:
        existing.trade_service_id = data.trade_service_id
    if data.is_active is not None:
        existing.is_active = data.is_active
    existing.updated_at = now
    updated = await repo.update(existing)
    return ScenarioResponse(
        id=updated.id,
        org_id=updated.org_id,
        name=updated.name,
        prompt=updated.prompt,
        response=updated.response,
        trigger_type=updated.trigger_type,
        trigger_value=updated.trigger_value,
        questions=updated.questions,
        outcome=updated.outcome,
        trade_service_id=updated.trade_service_id,
        is_active=updated.is_active,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: str,
    repo: ScenarioRepository = Depends(get_scenario_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    existing = await repo.get_by_id(scenario_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Scenario not found")
    await verify_org_access(existing.org_id, current_user, membership_repo)
    await repo.delete(scenario_id)
    return {"message": "Deleted"}
