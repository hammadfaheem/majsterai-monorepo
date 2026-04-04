"""Repository implementations for database access."""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.agent.entity import Agent as AgentEntity
from ....domain.call_history.entity import CallHistory as CallHistoryEntity
from ....domain.lead.entity import Activity as ActivityEntity, Inquiry as InquiryEntity, Lead as LeadEntity, Note as NoteEntity
from ....domain.membership.entity import Membership as MembershipEntity
from ....domain.membership_unavailability.entity import MembershipUnavailability as MembershipUnavailabilityEntity
from ....domain.organization.entity import Organization as OrganizationEntity
from ....domain.appointment.entity import Appointment as AppointmentEntity
from ....domain.department.entity import Department as DepartmentEntity
from ....domain.invoice.entity import Invoice as InvoiceEntity
from ....domain.schedule.entity import Schedule as ScheduleEntity
from ....domain.scenario.entity import Scenario as ScenarioEntity
from ....domain.transcript.entity import Transcript as TranscriptEntity
from ....domain.trade_category.entity import TradeCategory as TradeCategoryEntity
from ....domain.trade_service.entity import TradeService as TradeServiceEntity
from ....domain.tag_base.entity import TagBase as TagBaseEntity
from ....domain.task.entity import Task as TaskEntity
from ....domain.transfer.entity import Transfer as TransferEntity
from ....domain.user.entity import User as UserEntity
from ....domain.reminder.entity import Reminder as ReminderEntity
from ....domain.notification_type.entity import NotificationType as NotificationTypeEntity
from ....domain.notification_log.entity import NotificationLog as NotificationLogEntity
from ....domain.org_notification_recipient.entity import OrgNotificationRecipient as OrgNotificationRecipientEntity
from ....domain.lead_address.entity import LeadAddress as LeadAddressEntity
from ....domain.availability.entity import Availability as AvailabilityEntity
from ....db.models import (
    Activity,
    Agent,
    AgentActiveSession,
    AgentExtraPromptVersion,
    Appointment,
    Availability,
    CallHistory,
    Department,
    Invoice,
    Inquiry,
    Lead,
    LeadAddress,
    Membership,
    MembershipUnavailability,
    Note,
    Organization,
    Reminder,
    NotificationType,
    NotificationLog,
    OrgNotificationRecipient,
    Schedule,
    Scenario,
    SelectedCalendar,
    Transcript,
    Transfer,
    TagBase,
    Task,
    TradeCategory,
    TradeService,
    User,
)


class OrganizationRepository(ABC):
    """Abstract organization repository interface."""

    @abstractmethod
    async def create(self, organization: OrganizationEntity) -> OrganizationEntity:
        pass

    @abstractmethod
    async def get_by_id(self, org_id: str) -> OrganizationEntity | None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> OrganizationEntity | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[OrganizationEntity]:
        pass

    @abstractmethod
    async def list_by_member_user_id(self, user_id: str) -> list[OrganizationEntity]:
        pass

    @abstractmethod
    async def update(self, organization: OrganizationEntity) -> OrganizationEntity:
        pass


class AgentRepository(ABC):
    """Abstract agent repository interface."""

    @abstractmethod
    async def get_by_org_id(self, org_id: str) -> AgentEntity | None:
        pass

    @abstractmethod
    async def update(self, agent: AgentEntity) -> AgentEntity:
        pass

    @abstractmethod
    async def create(self, agent: AgentEntity) -> AgentEntity:
        pass


class CallHistoryRepository(ABC):
    """Abstract call history repository interface."""

    @abstractmethod
    async def create(self, call_history: CallHistoryEntity) -> CallHistoryEntity:
        pass

    @abstractmethod
    async def get_by_room_name(self, room_name: str) -> CallHistoryEntity | None:
        pass

    @abstractmethod
    async def list_by_org_id(
        self,
        org_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CallHistoryEntity]:
        pass

    @abstractmethod
    async def update(self, call_history: CallHistoryEntity) -> CallHistoryEntity:
        pass


class TranscriptRepository(ABC):
    """Abstract transcript repository interface."""

    @abstractmethod
    async def get_by_room_name(self, room_name: str) -> TranscriptEntity | None:
        pass


class UserRepository(ABC):
    """Abstract user repository interface."""

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[UserEntity]:
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> UserEntity:
        pass


class MembershipRepository(ABC):
    """Abstract membership repository interface."""

    @abstractmethod
    async def create(self, membership: MembershipEntity) -> MembershipEntity:
        pass

    @abstractmethod
    async def get_by_org_and_user(self, org_id: str, user_id: str) -> MembershipEntity | None:
        pass

    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[MembershipEntity]:
        pass

    @abstractmethod
    async def update(self, membership: MembershipEntity) -> MembershipEntity:
        pass

    @abstractmethod
    async def delete(self, membership_id: str) -> None:
        pass


class MembershipUnavailabilityRepository(ABC):
    """Abstract membership unavailability repository interface."""

    @abstractmethod
    async def create(self, unavailability: MembershipUnavailabilityEntity) -> MembershipUnavailabilityEntity:
        pass

    @abstractmethod
    async def get_by_id(self, unavailability_id: str) -> MembershipUnavailabilityEntity | None:
        pass

    @abstractmethod
    async def list_by_member_id(self, member_id: str) -> list[MembershipUnavailabilityEntity]:
        pass

    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[MembershipUnavailabilityEntity]:
        pass

    @abstractmethod
    async def update(self, unavailability: MembershipUnavailabilityEntity) -> MembershipUnavailabilityEntity:
        pass

    @abstractmethod
    async def delete(self, unavailability_id: str) -> None:
        pass


class LeadRepository(ABC):
    """Abstract lead repository interface."""

    @abstractmethod
    async def create(self, lead: LeadEntity) -> LeadEntity:
        pass

    @abstractmethod
    async def get_by_id(self, lead_id: str) -> LeadEntity | None:
        pass

    @abstractmethod
    async def update(self, lead: LeadEntity) -> LeadEntity:
        pass

    @abstractmethod
    async def list_by_org_id(
        self,
        org_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LeadEntity]:
        pass


class NoteRepository(ABC):
    """Abstract note repository interface."""

    @abstractmethod
    async def create(self, note: NoteEntity) -> NoteEntity:
        pass

    @abstractmethod
    async def get_by_lead_id(self, lead_id: str) -> list[NoteEntity]:
        pass


class ActivityRepository(ABC):
    """Abstract activity repository interface."""

    @abstractmethod
    async def create(self, activity: ActivityEntity) -> ActivityEntity:
        pass

    @abstractmethod
    async def list_by_lead_id(self, lead_id: str) -> list[ActivityEntity]:
        pass


class SQLAlchemyOrganizationRepository(OrganizationRepository):
    """SQLAlchemy implementation of OrganizationRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Organization) -> OrganizationEntity:
        """Convert SQLAlchemy model to domain entity."""
        return OrganizationEntity(
            id=model.id,
            name=model.name,
            slug=model.slug,
            time_zone=model.time_zone,
            country=model.country,
            currency=model.currency,
            settings=model.settings,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            stripe_plan=model.stripe_plan,
            stripe_customer_id=model.stripe_customer_id,
            default_schedule_id=model.default_schedule_id,
            public_scheduler_configurations=model.public_scheduler_configurations,
            tag=model.tag,
            seats=model.seats,
            addons=model.addons,
        )

    def _to_model(self, entity: OrganizationEntity) -> Organization:
        """Convert domain entity to SQLAlchemy model."""
        model = Organization(
            name=entity.name,
            slug=entity.slug,
            time_zone=entity.time_zone,
            country=entity.country,
            currency=entity.currency,
            settings=entity.settings,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            stripe_plan=entity.stripe_plan,
            stripe_customer_id=entity.stripe_customer_id,
            default_schedule_id=entity.default_schedule_id,
            public_scheduler_configurations=entity.public_scheduler_configurations,
            tag=entity.tag,
            seats=entity.seats,
            addons=entity.addons,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, organization: OrganizationEntity) -> OrganizationEntity:
        """Create a new organization."""
        # Generate UUID if not provided
        if not organization.id:
            from ....db.database import generate_uuid
            organization.id = generate_uuid()
        
        model = self._to_model(organization)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, org_id: str) -> OrganizationEntity | None:
        """Get organization by ID."""
        result = await self.session.execute(
            select(Organization).where(Organization.id == org_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> OrganizationEntity | None:
        """Get organization by slug."""
        result = await self.session.execute(
            select(Organization).where(Organization.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[OrganizationEntity]:
        """List all non-deleted organizations."""
        result = await self.session.execute(
            select(Organization)
            .where(Organization.deleted_at.is_(None))
            .order_by(Organization.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def list_by_member_user_id(self, user_id: str) -> list[OrganizationEntity]:
        """List organizations where the user has a membership."""
        result = await self.session.execute(
            select(Organization)
            .join(Membership, Organization.id == Membership.org_id)
            .where(Membership.user_id == user_id)
            .where(Organization.deleted_at.is_(None))
            .order_by(Organization.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, organization: OrganizationEntity) -> OrganizationEntity:
        """Update organization."""
        result = await self.session.execute(
            select(Organization).where(Organization.id == organization.id)
        )
        model = result.scalar_one()
        model.name = organization.name
        model.slug = organization.slug
        model.time_zone = organization.time_zone
        model.country = organization.country
        model.currency = organization.currency
        model.settings = organization.settings
        model.updated_at = organization.updated_at
        model.deleted_at = organization.deleted_at
        model.stripe_plan = organization.stripe_plan
        model.stripe_customer_id = organization.stripe_customer_id
        model.default_schedule_id = organization.default_schedule_id
        model.public_scheduler_configurations = organization.public_scheduler_configurations
        model.tag = organization.tag
        model.seats = organization.seats
        model.addons = organization.addons
        await self.session.flush()
        return self._to_entity(model)


class SQLAlchemyAgentRepository(AgentRepository):
    """SQLAlchemy implementation of AgentRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Agent) -> AgentEntity:
        """Convert SQLAlchemy model to domain entity."""
        return AgentEntity(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            prompt=model.prompt,
            extra_prompt=model.extra_prompt,
            is_custom_prompt=model.is_custom_prompt,
            llm_model=model.llm_model,
            stt_model=model.stt_model,
            tts_model=model.tts_model,
            settings=model.settings,
            variables=model.variables,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: AgentEntity) -> Agent:
        """Convert domain entity to SQLAlchemy model."""
        # Agent model uses auto-increment, so don't set id if it's 0
        model = Agent(
            org_id=entity.org_id,
            name=entity.name,
            prompt=entity.prompt,
            extra_prompt=entity.extra_prompt,
            is_custom_prompt=entity.is_custom_prompt,
            llm_model=entity.llm_model,
            stt_model=entity.stt_model,
            tts_model=entity.tts_model,
            settings=entity.settings,
            variables=entity.variables,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )
        # Only set id if it's a valid non-zero value (for updates)
        if entity.id and entity.id > 0:
            model.id = entity.id
        return model

    async def get_by_org_id(self, org_id: str) -> AgentEntity | None:
        """Get agent by organization ID."""
        result = await self.session.execute(
            select(Agent).where(
                Agent.org_id == org_id,
                Agent.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, agent: AgentEntity) -> AgentEntity:
        """Update agent."""
        result = await self.session.execute(
            select(Agent).where(Agent.id == agent.id)
        )
        model = result.scalar_one()
        model.name = agent.name
        model.prompt = agent.prompt
        model.extra_prompt = agent.extra_prompt
        model.is_custom_prompt = agent.is_custom_prompt
        model.llm_model = agent.llm_model
        model.stt_model = agent.stt_model
        model.tts_model = agent.tts_model
        model.settings = agent.settings
        model.variables = agent.variables
        model.status = agent.status
        model.updated_at = agent.updated_at
        model.deleted_at = agent.deleted_at
        await self.session.flush()
        return self._to_entity(model)

    async def create(self, agent: AgentEntity) -> AgentEntity:
        """Create a new agent."""
        model = self._to_model(agent)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)


class SQLAlchemyCallHistoryRepository(CallHistoryRepository):
    """SQLAlchemy implementation of CallHistoryRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: CallHistory) -> CallHistoryEntity:
        """Convert SQLAlchemy model to domain entity."""
        return CallHistoryEntity(
            id=model.id,
            room_name=model.room_name,
            org_id=model.org_id,
            agent_id=model.agent_id,
            direction=model.direction,
            from_phone_number=model.from_phone_number,
            to_phone_number=model.to_phone_number,
            start_time=model.start_time,
            end_time=model.end_time,
            duration=model.duration,
            status=model.status,
            summary=model.summary,
            transcript=None,
            analyzed_data=model.analyzed_data,
            extra_data=model.extra_data,
            twilio_call_sid=model.twilio_call_sid,
            function_calls=model.function_calls,
            cost=model.cost,
            total_metrics=model.total_metrics,
            variables=model.variables,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: CallHistoryEntity) -> CallHistory:
        """Convert domain entity to SQLAlchemy model."""
        # CallHistory model uses auto-increment, so don't set id if it's 0
        model = CallHistory(
            room_name=entity.room_name,
            org_id=entity.org_id,
            agent_id=entity.agent_id,
            direction=entity.direction,
            from_phone_number=entity.from_phone_number,
            to_phone_number=entity.to_phone_number,
            start_time=entity.start_time,
            end_time=entity.end_time,
            duration=entity.duration,
            status=entity.status,
            summary=entity.summary,
            analyzed_data=entity.analyzed_data,
            extra_data=entity.extra_data,
            twilio_call_sid=entity.twilio_call_sid,
            function_calls=entity.function_calls,
            cost=entity.cost,
            total_metrics=entity.total_metrics,
            variables=entity.variables,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        # Only set id if it's a valid non-zero value (for updates)
        if entity.id and entity.id > 0:
            model.id = entity.id
        return model

    async def create(self, call_history: CallHistoryEntity) -> CallHistoryEntity:
        """Create a new call history record."""
        model = self._to_model(call_history)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_room_name(self, room_name: str) -> CallHistoryEntity | None:
        """Get call history by room name."""
        result = await self.session.execute(
            select(CallHistory).where(CallHistory.room_name == room_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_org_id(
        self,
        org_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CallHistoryEntity]:
        """List call history for an organization."""
        result = await self.session.execute(
            select(CallHistory)
            .where(CallHistory.org_id == org_id)
            .order_by(CallHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, call_history: CallHistoryEntity) -> CallHistoryEntity:
        """Update call history."""
        result = await self.session.execute(
            select(CallHistory).where(CallHistory.id == call_history.id)
        )
        model = result.scalar_one()
        model.room_name = call_history.room_name
        model.org_id = call_history.org_id
        model.agent_id = call_history.agent_id
        model.direction = call_history.direction
        model.from_phone_number = call_history.from_phone_number
        model.to_phone_number = call_history.to_phone_number
        model.start_time = call_history.start_time
        model.end_time = call_history.end_time
        model.duration = call_history.duration
        model.status = call_history.status
        model.summary = call_history.summary
        model.transcript = call_history.transcript
        model.analyzed_data = call_history.analyzed_data
        model.extra_data = call_history.extra_data
        model.twilio_call_sid = call_history.twilio_call_sid
        model.function_calls = call_history.function_calls
        model.cost = call_history.cost
        model.total_metrics = call_history.total_metrics
        model.variables = call_history.variables
        model.updated_at = call_history.updated_at
        await self.session.flush()
        return self._to_entity(model)


class ScenarioRepository(ABC):
    """Abstract scenario repository interface."""

    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[ScenarioEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, scenario_id: str) -> ScenarioEntity | None:
        pass

    @abstractmethod
    async def create(self, scenario: ScenarioEntity) -> ScenarioEntity:
        pass

    @abstractmethod
    async def update(self, scenario: ScenarioEntity) -> ScenarioEntity:
        pass

    @abstractmethod
    async def delete(self, scenario_id: str) -> bool:
        pass


class TransferRepository(ABC):
    """Abstract transfer repository interface."""

    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[TransferEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, transfer_id: str) -> TransferEntity | None:
        pass

    @abstractmethod
    async def create(self, transfer: TransferEntity) -> TransferEntity:
        pass

    @abstractmethod
    async def update(self, transfer: TransferEntity) -> TransferEntity:
        pass

    @abstractmethod
    async def delete(self, transfer_id: str) -> bool:
        pass


class SQLAlchemyScenarioRepository(ScenarioRepository):
    """SQLAlchemy implementation of ScenarioRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Scenario) -> ScenarioEntity:
        return ScenarioEntity(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            prompt=model.prompt,
            response=model.response,
            trigger_type=model.trigger_type,
            trigger_value=model.trigger_value,
            questions=model.questions,
            outcome=model.outcome,
            trade_service_id=model.trade_service_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[ScenarioEntity]:
        result = await self.session.execute(
            select(Scenario).where(Scenario.org_id == org_id).order_by(Scenario.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, scenario_id: str) -> ScenarioEntity | None:
        result = await self.session.execute(select(Scenario).where(Scenario.id == scenario_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, scenario: ScenarioEntity) -> ScenarioEntity:
        model = Scenario(
            id=scenario.id,
            org_id=scenario.org_id,
            name=scenario.name,
            prompt=scenario.prompt,
            response=scenario.response,
            trigger_type=scenario.trigger_type,
            trigger_value=scenario.trigger_value,
            questions=scenario.questions,
            outcome=scenario.outcome,
            trade_service_id=scenario.trade_service_id,
            is_active=scenario.is_active,
            created_at=scenario.created_at,
            updated_at=scenario.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, scenario: ScenarioEntity) -> ScenarioEntity:
        result = await self.session.execute(select(Scenario).where(Scenario.id == scenario.id))
        model = result.scalar_one()
        model.name = scenario.name
        model.prompt = scenario.prompt
        model.response = scenario.response
        model.trigger_type = scenario.trigger_type
        model.trigger_value = scenario.trigger_value
        model.questions = scenario.questions
        model.outcome = scenario.outcome
        model.trade_service_id = scenario.trade_service_id
        model.is_active = scenario.is_active
        model.updated_at = scenario.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, scenario_id: str) -> bool:
        result = await self.session.execute(delete(Scenario).where(Scenario.id == scenario_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class SQLAlchemyTransferRepository(TransferRepository):
    """SQLAlchemy implementation of TransferRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Transfer) -> TransferEntity:
        return TransferEntity(
            id=model.id,
            org_id=model.org_id,
            label=model.label,
            method=model.method,
            destination_type=model.destination_type,
            destination=model.destination,
            conditions=model.conditions,
            summary_format=model.summary_format,
            settings=model.settings,
            scenario_id=model.scenario_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[TransferEntity]:
        result = await self.session.execute(
            select(Transfer).where(Transfer.org_id == org_id).order_by(Transfer.label)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, transfer_id: str) -> TransferEntity | None:
        result = await self.session.execute(select(Transfer).where(Transfer.id == transfer_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, transfer: TransferEntity) -> TransferEntity:
        model = Transfer(
            id=transfer.id,
            org_id=transfer.org_id,
            label=transfer.label,
            method=transfer.method,
            destination_type=transfer.destination_type,
            destination=transfer.destination,
            conditions=transfer.conditions,
            summary_format=transfer.summary_format,
            settings=transfer.settings,
            scenario_id=transfer.scenario_id,
            created_at=transfer.created_at,
            updated_at=transfer.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, transfer: TransferEntity) -> TransferEntity:
        result = await self.session.execute(select(Transfer).where(Transfer.id == transfer.id))
        model = result.scalar_one()
        model.label = transfer.label
        model.method = transfer.method
        model.destination_type = transfer.destination_type
        model.destination = transfer.destination
        model.conditions = transfer.conditions
        model.summary_format = transfer.summary_format
        model.settings = transfer.settings
        model.scenario_id = transfer.scenario_id
        model.updated_at = transfer.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, transfer_id: str) -> bool:
        result = await self.session.execute(delete(Transfer).where(Transfer.id == transfer_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class ScheduleRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[ScheduleEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, schedule_id: int) -> ScheduleEntity | None:
        pass

    @abstractmethod
    async def create(self, schedule: ScheduleEntity) -> ScheduleEntity:
        pass

    @abstractmethod
    async def update(self, schedule: ScheduleEntity) -> ScheduleEntity:
        pass

    @abstractmethod
    async def delete(self, schedule_id: int) -> bool:
        pass


class DepartmentRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[DepartmentEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, department_id: int) -> DepartmentEntity | None:
        pass

    @abstractmethod
    async def create(self, department: DepartmentEntity) -> DepartmentEntity:
        pass

    @abstractmethod
    async def update(self, department: DepartmentEntity) -> DepartmentEntity:
        pass

    @abstractmethod
    async def delete(self, department_id: int) -> bool:
        pass


class AppointmentRepository(ABC):
    @abstractmethod
    async def list_by_org_id(
        self,
        org_id: str,
        limit: int,
        offset: int,
        lead_id: str | None = None,
        start_from: int | None = None,
        end_before: int | None = None,
        statuses: list[str] | None = None,
        include_deleted: bool = False,
    ) -> list[AppointmentEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, appointment_id: str) -> AppointmentEntity | None:
        pass

    @abstractmethod
    async def get_by_reference_id(self, reference_id: str) -> AppointmentEntity | None:
        pass

    @abstractmethod
    async def create(self, appointment: AppointmentEntity) -> AppointmentEntity:
        pass

    @abstractmethod
    async def update(self, appointment: AppointmentEntity) -> AppointmentEntity:
        pass

    @abstractmethod
    async def soft_delete(self, appointment_id: str, deleted_at: int) -> bool:
        pass

    @abstractmethod
    async def delete(self, appointment_id: str) -> bool:
        pass


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Schedule) -> ScheduleEntity:
        return ScheduleEntity(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            time_zone=model.time_zone,
            department_id=model.department_id,
        )

    async def list_all(self) -> list[ScheduleEntity]:
        result = await self.session.execute(select(Schedule).order_by(Schedule.name))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, schedule_id: int) -> ScheduleEntity | None:
        result = await self.session.execute(select(Schedule).where(Schedule.id == schedule_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, schedule: ScheduleEntity) -> ScheduleEntity:
        model = Schedule(
            org_id=schedule.org_id,
            name=schedule.name,
            time_zone=schedule.time_zone,
            department_id=schedule.department_id,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, schedule: ScheduleEntity) -> ScheduleEntity:
        result = await self.session.execute(select(Schedule).where(Schedule.id == schedule.id))
        model = result.scalar_one()
        model.org_id = schedule.org_id
        model.name = schedule.name
        model.time_zone = schedule.time_zone
        model.department_id = schedule.department_id
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, schedule_id: int) -> bool:
        result = await self.session.execute(delete(Schedule).where(Schedule.id == schedule_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class SQLAlchemyDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Department) -> DepartmentEntity:
        return DepartmentEntity(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            description=model.description,
            default_schedule_id=model.default_schedule_id,
            is_active=model.is_active,
            max_concurrent_calls=model.max_concurrent_calls,
            escalation_timeout=model.escalation_timeout,
            escalation_settings=model.escalation_settings,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[DepartmentEntity]:
        result = await self.session.execute(
            select(Department).where(Department.org_id == org_id).order_by(Department.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, department_id: int) -> DepartmentEntity | None:
        result = await self.session.execute(select(Department).where(Department.id == department_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, department: DepartmentEntity) -> DepartmentEntity:
        model = Department(
            org_id=department.org_id,
            name=department.name,
            description=department.description,
            default_schedule_id=department.default_schedule_id,
            is_active=department.is_active,
            max_concurrent_calls=department.max_concurrent_calls,
            escalation_timeout=department.escalation_timeout,
            escalation_settings=department.escalation_settings,
            created_at=department.created_at,
            updated_at=department.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, department: DepartmentEntity) -> DepartmentEntity:
        result = await self.session.execute(select(Department).where(Department.id == department.id))
        model = result.scalar_one()
        model.name = department.name
        model.description = department.description
        model.default_schedule_id = department.default_schedule_id
        model.is_active = department.is_active
        model.max_concurrent_calls = department.max_concurrent_calls
        model.escalation_timeout = department.escalation_timeout
        model.escalation_settings = department.escalation_settings
        model.updated_at = department.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, department_id: int) -> bool:
        result = await self.session.execute(delete(Department).where(Department.id == department_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class SQLAlchemyAppointmentRepository(AppointmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Appointment) -> AppointmentEntity:
        return AppointmentEntity(
            id=model.id,
            org_id=model.org_id,
            serial_id=model.serial_id,
            start=model.start,
            end=model.end,
            title=model.title,
            description=model.description,
            status=model.status,
            lead_id=model.lead_id,
            inquiry_id=model.inquiry_id,
            trade_service_id=model.trade_service_id,
            lead_address_id=model.lead_address_id,
            selected_calendar_id=model.selected_calendar_id,
            attendees=model.attendees,
            is_rescheduled=model.is_rescheduled,
            is_created_by_sophiie=model.is_created_by_sophiie,
            notes=model.notes,
            customer_notes=model.customer_notes,
            customer_cancellation_reason=model.customer_cancellation_reason,
            summary=model.summary,
            photos=model.photos,
            reference_id=model.reference_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    async def list_by_org_id(
        self,
        org_id: str,
        limit: int = 100,
        offset: int = 0,
        lead_id: str | None = None,
        start_from: int | None = None,
        end_before: int | None = None,
        statuses: list[str] | None = None,
        include_deleted: bool = False,
    ) -> list[AppointmentEntity]:
        q = select(Appointment).where(Appointment.org_id == org_id)
        if not include_deleted:
            q = q.where(Appointment.deleted_at.is_(None))
        if lead_id is not None:
            q = q.where(Appointment.lead_id == lead_id)
        if start_from is not None:
            q = q.where(Appointment.start >= start_from)
        if end_before is not None:
            q = q.where(Appointment.end <= end_before)
        if statuses:
            q = q.where(Appointment.status.in_(statuses))
        q = q.order_by(Appointment.start.desc()).limit(limit).offset(offset)
        result = await self.session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, appointment_id: str) -> AppointmentEntity | None:
        result = await self.session.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_reference_id(self, reference_id: str) -> AppointmentEntity | None:
        result = await self.session.execute(
            select(Appointment).where(Appointment.reference_id == reference_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, appointment: AppointmentEntity) -> AppointmentEntity:
        model = Appointment(
            id=appointment.id,
            org_id=appointment.org_id,
            serial_id=appointment.serial_id,
            start=appointment.start,
            end=appointment.end,
            title=appointment.title,
            description=appointment.description,
            status=appointment.status,
            lead_id=appointment.lead_id,
            inquiry_id=appointment.inquiry_id,
            trade_service_id=appointment.trade_service_id,
            lead_address_id=appointment.lead_address_id,
            selected_calendar_id=appointment.selected_calendar_id,
            attendees=appointment.attendees,
            is_rescheduled=appointment.is_rescheduled,
            is_created_by_sophiie=appointment.is_created_by_sophiie,
            notes=appointment.notes,
            customer_notes=appointment.customer_notes,
            customer_cancellation_reason=appointment.customer_cancellation_reason,
            summary=appointment.summary,
            photos=appointment.photos,
            reference_id=appointment.reference_id,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, appointment: AppointmentEntity) -> AppointmentEntity:
        result = await self.session.execute(
            select(Appointment).where(Appointment.id == appointment.id)
        )
        model = result.scalar_one()
        model.start = appointment.start
        model.end = appointment.end
        model.title = appointment.title
        model.description = appointment.description
        model.status = appointment.status
        model.lead_id = appointment.lead_id
        model.inquiry_id = appointment.inquiry_id
        model.trade_service_id = appointment.trade_service_id
        model.lead_address_id = appointment.lead_address_id
        model.selected_calendar_id = appointment.selected_calendar_id
        model.attendees = appointment.attendees
        model.is_rescheduled = appointment.is_rescheduled
        model.is_created_by_sophiie = appointment.is_created_by_sophiie
        model.notes = appointment.notes
        model.customer_notes = appointment.customer_notes
        model.customer_cancellation_reason = appointment.customer_cancellation_reason
        model.summary = appointment.summary
        model.photos = appointment.photos
        model.reference_id = appointment.reference_id
        model.updated_at = appointment.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def soft_delete(self, appointment_id: str, deleted_at: int) -> bool:
        result = await self.session.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        model.deleted_at = deleted_at
        await self.session.flush()
        return True

    async def delete(self, appointment_id: str) -> bool:
        result = await self.session.execute(
            delete(Appointment).where(Appointment.id == appointment_id)
        )
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class InvoiceRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str, limit: int, offset: int) -> list[InvoiceEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, invoice_id: str) -> InvoiceEntity | None:
        pass

    @abstractmethod
    async def create(self, invoice: InvoiceEntity) -> InvoiceEntity:
        pass

    @abstractmethod
    async def update(self, invoice: InvoiceEntity) -> InvoiceEntity:
        pass

    @abstractmethod
    async def delete(self, invoice_id: str) -> bool:
        pass


class SQLAlchemyInvoiceRepository(InvoiceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Invoice) -> InvoiceEntity:
        return InvoiceEntity(
            id=model.id,
            org_id=model.org_id,
            lead_id=model.lead_id,
            index=model.index,
            status=model.status,
            date=model.date,
            due_date=model.due_date,
            tax_type=model.tax_type,
            reference=model.reference,
            notes=model.notes,
            accept_credit_card=model.accept_credit_card,
            reminder_sent=model.reminder_sent,
            approved_at=model.approved_at,
            sent_at=model.sent_at,
            external_id=model.external_id,
            last_synced_at=model.last_synced_at,
            is_sync_failed=model.is_sync_failed,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str, limit: int = 100, offset: int = 0) -> list[InvoiceEntity]:
        result = await self.session.execute(
            select(Invoice).where(Invoice.org_id == org_id).order_by(Invoice.created_at.desc()).limit(limit).offset(offset)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, invoice_id: str) -> InvoiceEntity | None:
        result = await self.session.execute(select(Invoice).where(Invoice.id == invoice_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, invoice: InvoiceEntity) -> InvoiceEntity:
        model = Invoice(
            id=invoice.id,
            org_id=invoice.org_id,
            lead_id=invoice.lead_id,
            index=invoice.index,
            status=invoice.status,
            date=invoice.date,
            due_date=invoice.due_date,
            tax_type=invoice.tax_type,
            reference=invoice.reference,
            notes=invoice.notes,
            accept_credit_card=invoice.accept_credit_card,
            reminder_sent=invoice.reminder_sent,
            approved_at=invoice.approved_at,
            sent_at=invoice.sent_at,
            external_id=invoice.external_id,
            last_synced_at=invoice.last_synced_at,
            is_sync_failed=invoice.is_sync_failed,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, invoice: InvoiceEntity) -> InvoiceEntity:
        result = await self.session.execute(select(Invoice).where(Invoice.id == invoice.id))
        model = result.scalar_one()
        model.status = invoice.status
        model.date = invoice.date
        model.due_date = invoice.due_date
        model.tax_type = invoice.tax_type
        model.reference = invoice.reference
        model.notes = invoice.notes
        model.accept_credit_card = invoice.accept_credit_card
        model.reminder_sent = invoice.reminder_sent
        model.approved_at = invoice.approved_at
        model.sent_at = invoice.sent_at
        model.external_id = invoice.external_id
        model.last_synced_at = invoice.last_synced_at
        model.is_sync_failed = invoice.is_sync_failed
        model.updated_at = invoice.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, invoice_id: str) -> bool:
        result = await self.session.execute(delete(Invoice).where(Invoice.id == invoice_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class TradeCategoryRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[TradeCategoryEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, category_id: int) -> TradeCategoryEntity | None:
        pass

    @abstractmethod
    async def create(self, category: TradeCategoryEntity) -> TradeCategoryEntity:
        pass

    @abstractmethod
    async def update(self, category: TradeCategoryEntity) -> TradeCategoryEntity:
        pass

    @abstractmethod
    async def delete(self, category_id: int) -> bool:
        pass


class TradeServiceRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[TradeServiceEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, service_id: int) -> TradeServiceEntity | None:
        pass

    @abstractmethod
    async def create(self, service: TradeServiceEntity) -> TradeServiceEntity:
        pass

    @abstractmethod
    async def update(self, service: TradeServiceEntity) -> TradeServiceEntity:
        pass

    @abstractmethod
    async def delete(self, service_id: int) -> bool:
        pass


class SQLAlchemyTradeCategoryRepository(TradeCategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TradeCategory) -> TradeCategoryEntity:
        return TradeCategoryEntity(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            type=model.type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[TradeCategoryEntity]:
        result = await self.session.execute(
            select(TradeCategory).where(TradeCategory.org_id == org_id).order_by(TradeCategory.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, category_id: int) -> TradeCategoryEntity | None:
        result = await self.session.execute(select(TradeCategory).where(TradeCategory.id == category_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, category: TradeCategoryEntity) -> TradeCategoryEntity:
        model = TradeCategory(
            org_id=category.org_id,
            name=category.name,
            type=category.type,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, category: TradeCategoryEntity) -> TradeCategoryEntity:
        result = await self.session.execute(select(TradeCategory).where(TradeCategory.id == category.id))
        model = result.scalar_one()
        model.name = category.name
        model.type = category.type
        model.updated_at = category.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, category_id: int) -> bool:
        result = await self.session.execute(delete(TradeCategory).where(TradeCategory.id == category_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class SQLAlchemyTradeServiceRepository(TradeServiceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TradeService) -> TradeServiceEntity:
        return TradeServiceEntity(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            description=model.description,
            duration=model.duration,
            duration_unit=model.duration_unit,
            followup_questions=model.followup_questions,
            pricing_mode=model.pricing_mode,
            fixed_price=model.fixed_price,
            hourly_rate=model.hourly_rate,
            min_price=model.min_price,
            max_price=model.max_price,
            call_out_fee=model.call_out_fee,
            plus_gst=model.plus_gst,
            plus_materials=model.plus_materials,
            is_disclose_price=model.is_disclose_price,
            custom_price_response=model.custom_price_response,
            is_active=model.is_active,
            trade_category_id=model.trade_category_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[TradeServiceEntity]:
        result = await self.session.execute(
            select(TradeService).where(TradeService.org_id == org_id).order_by(TradeService.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, service_id: int) -> TradeServiceEntity | None:
        result = await self.session.execute(select(TradeService).where(TradeService.id == service_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, service: TradeServiceEntity) -> TradeServiceEntity:
        model = TradeService(
            org_id=service.org_id,
            name=service.name,
            description=service.description,
            duration=service.duration,
            duration_unit=service.duration_unit,
            followup_questions=service.followup_questions,
            pricing_mode=service.pricing_mode,
            fixed_price=service.fixed_price,
            hourly_rate=service.hourly_rate,
            min_price=service.min_price,
            max_price=service.max_price,
            call_out_fee=service.call_out_fee,
            plus_gst=service.plus_gst,
            plus_materials=service.plus_materials,
            is_disclose_price=service.is_disclose_price,
            custom_price_response=service.custom_price_response,
            is_active=service.is_active,
            trade_category_id=service.trade_category_id,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, service: TradeServiceEntity) -> TradeServiceEntity:
        result = await self.session.execute(select(TradeService).where(TradeService.id == service.id))
        model = result.scalar_one()
        model.name = service.name
        model.description = service.description
        model.duration = service.duration
        model.duration_unit = service.duration_unit
        model.followup_questions = service.followup_questions
        model.pricing_mode = service.pricing_mode
        model.fixed_price = service.fixed_price
        model.hourly_rate = service.hourly_rate
        model.min_price = service.min_price
        model.max_price = service.max_price
        model.call_out_fee = service.call_out_fee
        model.plus_gst = service.plus_gst
        model.plus_materials = service.plus_materials
        model.is_disclose_price = service.is_disclose_price
        model.custom_price_response = service.custom_price_response
        model.is_active = service.is_active
        model.trade_category_id = service.trade_category_id
        model.updated_at = service.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, service_id: int) -> bool:
        result = await self.session.execute(delete(TradeService).where(TradeService.id == service_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class TagBaseRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[TagBaseEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, tag_base_id: str) -> TagBaseEntity | None:
        pass

    @abstractmethod
    async def create(self, tag_base: TagBaseEntity) -> TagBaseEntity:
        pass

    @abstractmethod
    async def update(self, tag_base: TagBaseEntity) -> TagBaseEntity:
        pass

    @abstractmethod
    async def delete(self, tag_base_id: str) -> bool:
        pass


class TaskRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str, lead_id: str | None) -> list[TaskEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, task_id: str) -> TaskEntity | None:
        pass

    @abstractmethod
    async def create(self, task: TaskEntity) -> TaskEntity:
        pass

    @abstractmethod
    async def update(self, task: TaskEntity) -> TaskEntity:
        pass

    @abstractmethod
    async def delete(self, task_id: str) -> bool:
        pass


class SQLAlchemyTagBaseRepository(TagBaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: TagBase) -> TagBaseEntity:
        return TagBaseEntity(
            id=model.id,
            org_id=model.org_id,
            value=model.value,
            color=model.color,
            type=model.type,
            description=model.description,
            external_id=model.external_id,
            external_type=model.external_type,
            is_enabled=model.is_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[TagBaseEntity]:
        result = await self.session.execute(
            select(TagBase).where(TagBase.org_id == org_id).order_by(TagBase.value)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, tag_base_id: str) -> TagBaseEntity | None:
        result = await self.session.execute(select(TagBase).where(TagBase.id == tag_base_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, tag_base: TagBaseEntity) -> TagBaseEntity:
        model = TagBase(
            id=tag_base.id,
            org_id=tag_base.org_id,
            value=tag_base.value,
            color=tag_base.color,
            type=tag_base.type,
            description=tag_base.description,
            external_id=tag_base.external_id,
            external_type=tag_base.external_type,
            is_enabled=tag_base.is_enabled,
            created_at=tag_base.created_at,
            updated_at=tag_base.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, tag_base: TagBaseEntity) -> TagBaseEntity:
        result = await self.session.execute(select(TagBase).where(TagBase.id == tag_base.id))
        model = result.scalar_one()
        model.value = tag_base.value
        model.color = tag_base.color
        model.type = tag_base.type
        model.description = tag_base.description
        model.external_id = tag_base.external_id
        model.external_type = tag_base.external_type
        model.is_enabled = tag_base.is_enabled
        model.updated_at = tag_base.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, tag_base_id: str) -> bool:
        result = await self.session.execute(delete(TagBase).where(TagBase.id == tag_base_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Task) -> TaskEntity:
        return TaskEntity(
            id=model.id,
            org_id=model.org_id,
            title=model.title,
            is_completed=model.is_completed,
            type=model.type,
            inquiry_id=model.inquiry_id,
            lead_id=model.lead_id,
            assigned_member_id=model.assigned_member_id,
            is_created_by_sophiie=model.is_created_by_sophiie,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str, lead_id: str | None = None) -> list[TaskEntity]:
        q = select(Task).where(Task.org_id == org_id)
        if lead_id is not None:
            q = q.where(Task.lead_id == lead_id)
        q = q.order_by(Task.created_at.desc())
        result = await self.session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, task_id: str) -> TaskEntity | None:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, task: TaskEntity) -> TaskEntity:
        model = Task(
            id=task.id,
            org_id=task.org_id,
            title=task.title,
            is_completed=task.is_completed,
            type=task.type,
            inquiry_id=task.inquiry_id,
            lead_id=task.lead_id,
            assigned_member_id=task.assigned_member_id,
            is_created_by_sophiie=task.is_created_by_sophiie,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, task: TaskEntity) -> TaskEntity:
        result = await self.session.execute(select(Task).where(Task.id == task.id))
        model = result.scalar_one()
        model.title = task.title
        model.is_completed = task.is_completed
        model.type = task.type
        model.inquiry_id = task.inquiry_id
        model.lead_id = task.lead_id
        model.assigned_member_id = task.assigned_member_id
        model.is_created_by_sophiie = task.is_created_by_sophiie
        model.updated_at = task.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, task_id: str) -> bool:
        result = await self.session.execute(delete(Task).where(Task.id == task_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


# --- Reminder ---
class ReminderRepository(ABC):
    @abstractmethod
    async def list_by_org(self, org_id: str, lead_id: str | None = None, user_id: str | None = None) -> list[ReminderEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, reminder_id: str) -> ReminderEntity | None:
        pass

    @abstractmethod
    async def create(self, reminder: ReminderEntity) -> ReminderEntity:
        pass

    @abstractmethod
    async def update(self, reminder: ReminderEntity) -> ReminderEntity:
        pass

    @abstractmethod
    async def delete(self, reminder_id: str) -> bool:
        pass


class SQLAlchemyReminderRepository(ReminderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Reminder) -> ReminderEntity:
        return ReminderEntity(
            id=model.id,
            lead_id=model.lead_id,
            appointment_id=model.appointment_id,
            user_id=model.user_id,
            datetime=model.datetime,
            notes=model.notes,
            notes_type=model.notes_type,
            priority=model.priority,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org(
        self, org_id: str, lead_id: str | None = None, user_id: str | None = None
    ) -> list[ReminderEntity]:
        from sqlalchemy import or_
        lead_ids = select(Lead.id).where(Lead.org_id == org_id)
        appt_ids = select(Appointment.id).where(Appointment.org_id == org_id)
        q = select(Reminder).where(
            or_(
                Reminder.lead_id.in_(lead_ids),
                Reminder.appointment_id.in_(appt_ids),
            )
        )
        if lead_id is not None:
            q = q.where(Reminder.lead_id == lead_id)
        if user_id is not None:
            q = q.where(Reminder.user_id == user_id)
        q = q.order_by(Reminder.datetime.asc().nullslast())
        result = await self.session.execute(q)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, reminder_id: str) -> ReminderEntity | None:
        result = await self.session.execute(select(Reminder).where(Reminder.id == reminder_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, reminder: ReminderEntity) -> ReminderEntity:
        model = Reminder(
            id=reminder.id,
            lead_id=reminder.lead_id,
            appointment_id=reminder.appointment_id,
            user_id=reminder.user_id,
            datetime=reminder.datetime,
            notes=reminder.notes,
            notes_type=reminder.notes_type,
            priority=reminder.priority,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, reminder: ReminderEntity) -> ReminderEntity:
        result = await self.session.execute(select(Reminder).where(Reminder.id == reminder.id))
        model = result.scalar_one()
        model.lead_id = reminder.lead_id
        model.appointment_id = reminder.appointment_id
        model.user_id = reminder.user_id
        model.datetime = reminder.datetime
        model.notes = reminder.notes
        model.notes_type = reminder.notes_type
        model.priority = reminder.priority
        model.updated_at = reminder.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, reminder_id: str) -> bool:
        result = await self.session.execute(delete(Reminder).where(Reminder.id == reminder_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


# --- NotificationType ---
class NotificationTypeRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[NotificationTypeEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, notification_type_id: str) -> NotificationTypeEntity | None:
        pass

    @abstractmethod
    async def update(self, entity: NotificationTypeEntity) -> NotificationTypeEntity:
        pass


class SQLAlchemyNotificationTypeRepository(NotificationTypeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: NotificationType) -> NotificationTypeEntity:
        return NotificationTypeEntity(
            id=model.id,
            org_id=model.org_id,
            value=model.value,
            template=model.template,
            channels=model.channels,
            schedule=model.schedule,
            enabled=model.enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[NotificationTypeEntity]:
        result = await self.session.execute(
            select(NotificationType).where(NotificationType.org_id == org_id).order_by(NotificationType.value)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, notification_type_id: str) -> NotificationTypeEntity | None:
        result = await self.session.execute(select(NotificationType).where(NotificationType.id == notification_type_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, entity: NotificationTypeEntity) -> NotificationTypeEntity:
        result = await self.session.execute(select(NotificationType).where(NotificationType.id == entity.id))
        model = result.scalar_one()
        model.value = entity.value
        model.template = entity.template
        model.channels = entity.channels
        model.schedule = entity.schedule
        model.enabled = entity.enabled
        model.updated_at = entity.updated_at
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)


# --- NotificationLog ---
class NotificationLogRepository(ABC):
    @abstractmethod
    async def list_recent(self, limit: int = 100, offset: int = 0) -> list[NotificationLogEntity]:
        pass


class SQLAlchemyNotificationLogRepository(NotificationLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: NotificationLog) -> NotificationLogEntity:
        return NotificationLogEntity(
            id=model.id,
            type=model.type,
            channel=model.channel,
            lead_id=model.lead_id,
            target_id=model.target_id,
            sent=model.sent,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_recent(self, limit: int = 100, offset: int = 0) -> list[NotificationLogEntity]:
        result = await self.session.execute(
            select(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(limit).offset(offset)
        )
        return [self._to_entity(m) for m in result.scalars().all()]


# --- OrgNotificationRecipient ---
class OrgNotificationRecipientRepository(ABC):
    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[OrgNotificationRecipientEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, recipient_id: str) -> OrgNotificationRecipientEntity | None:
        pass

    @abstractmethod
    async def update(self, entity: OrgNotificationRecipientEntity) -> OrgNotificationRecipientEntity:
        pass


class SQLAlchemyOrgNotificationRecipientRepository(OrgNotificationRecipientRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: OrgNotificationRecipient) -> OrgNotificationRecipientEntity:
        return OrgNotificationRecipientEntity(
            id=model.id,
            member_id=model.member_id,
            sms=model.sms,
            email=model.email,
            sources=model.sources,
            all_tags=model.all_tags,
            is_enabled=model.is_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_org_id(self, org_id: str) -> list[OrgNotificationRecipientEntity]:
        result = await self.session.execute(
            select(OrgNotificationRecipient)
            .join(Membership, OrgNotificationRecipient.member_id == Membership.id)
            .where(Membership.org_id == org_id)
            .order_by(OrgNotificationRecipient.id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, recipient_id: str) -> OrgNotificationRecipientEntity | None:
        result = await self.session.execute(
            select(OrgNotificationRecipient).where(OrgNotificationRecipient.id == recipient_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, entity: OrgNotificationRecipientEntity) -> OrgNotificationRecipientEntity:
        result = await self.session.execute(
            select(OrgNotificationRecipient).where(OrgNotificationRecipient.id == entity.id)
        )
        model = result.scalar_one()
        model.sms = entity.sms
        model.email = entity.email
        model.sources = entity.sources
        model.all_tags = entity.all_tags
        model.is_enabled = entity.is_enabled
        model.updated_at = entity.updated_at
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)


# --- LeadAddress ---
class LeadAddressRepository(ABC):
    @abstractmethod
    async def list_by_lead_id(self, lead_id: str) -> list[LeadAddressEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, lead_address_id: int) -> LeadAddressEntity | None:
        pass

    @abstractmethod
    async def create(self, entity: LeadAddressEntity) -> LeadAddressEntity:
        pass

    @abstractmethod
    async def delete(self, lead_address_id: int) -> bool:
        pass


class SQLAlchemyLeadAddressRepository(LeadAddressRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: LeadAddress) -> LeadAddressEntity:
        return LeadAddressEntity(
            id=model.id,
            address_id=model.address_id,
            lead_id=model.lead_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_lead_id(self, lead_id: str) -> list[LeadAddressEntity]:
        result = await self.session.execute(
            select(LeadAddress).where(LeadAddress.lead_id == lead_id).order_by(LeadAddress.id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, lead_address_id: int) -> LeadAddressEntity | None:
        result = await self.session.execute(select(LeadAddress).where(LeadAddress.id == lead_address_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: LeadAddressEntity) -> LeadAddressEntity:
        model = LeadAddress(
            address_id=entity.address_id,
            lead_id=entity.lead_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, lead_address_id: int) -> bool:
        result = await self.session.execute(delete(LeadAddress).where(LeadAddress.id == lead_address_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


# --- Availability ---
class AvailabilityRepository(ABC):
    @abstractmethod
    async def list_by_schedule_id(self, schedule_id: int) -> list[AvailabilityEntity]:
        pass

    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[AvailabilityEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, availability_id: int) -> AvailabilityEntity | None:
        pass

    @abstractmethod
    async def create(self, entity: AvailabilityEntity) -> AvailabilityEntity:
        pass

    @abstractmethod
    async def update(self, entity: AvailabilityEntity) -> AvailabilityEntity:
        pass

    @abstractmethod
    async def delete(self, availability_id: int) -> bool:
        pass


class SQLAlchemyAvailabilityRepository(AvailabilityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Availability) -> AvailabilityEntity:
        return AvailabilityEntity(
            id=model.id,
            schedule_id=model.schedule_id,
            days=model.days,
            start_time=model.start_time,
            end_time=model.end_time,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_by_schedule_id(self, schedule_id: int) -> list[AvailabilityEntity]:
        result = await self.session.execute(
            select(Availability).where(Availability.schedule_id == schedule_id).order_by(Availability.id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_org_id(self, org_id: str) -> list[AvailabilityEntity]:
        result = await self.session.execute(
            select(Availability)
            .join(Schedule, Availability.schedule_id == Schedule.id)
            .where(Schedule.org_id == org_id)
            .order_by(Availability.schedule_id, Availability.id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, availability_id: int) -> AvailabilityEntity | None:
        result = await self.session.execute(select(Availability).where(Availability.id == availability_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: AvailabilityEntity) -> AvailabilityEntity:
        model = Availability(
            schedule_id=entity.schedule_id,
            days=entity.days,
            start_time=entity.start_time,
            end_time=entity.end_time,
            user_id=entity.user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: AvailabilityEntity) -> AvailabilityEntity:
        result = await self.session.execute(select(Availability).where(Availability.id == entity.id))
        model = result.scalar_one()
        model.schedule_id = entity.schedule_id
        model.days = entity.days
        model.start_time = entity.start_time
        model.end_time = entity.end_time
        model.user_id = entity.user_id
        model.updated_at = entity.updated_at
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, availability_id: int) -> bool:
        result = await self.session.execute(delete(Availability).where(Availability.id == availability_id))
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0


class SQLAlchemyTranscriptRepository(TranscriptRepository):
    """SQLAlchemy implementation of TranscriptRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Transcript) -> TranscriptEntity:
        """Convert SQLAlchemy model to domain entity."""
        return TranscriptEntity(
            id=model.id,
            room_name=model.room_name,
            org_id=model.org_id,
            transcript=model.transcript,
            segments=model.segments,
            sentiment=model.sentiment,
            keywords=model.keywords,
            summary=model.summary,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_room_name(self, room_name: str) -> TranscriptEntity | None:
        """Get transcript by room name."""
        result = await self.session.execute(
            select(Transcript).where(Transcript.room_name == room_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: User) -> UserEntity:
        """Convert SQLAlchemy model to domain entity."""
        return UserEntity(
            id=model.id,
            email=model.email,
            name=model.name,
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            phone=model.phone,
            role=model.role,
            email_verified=model.email_verified,
            phone_verified=model.phone_verified,
        )

    def _to_model(self, entity: UserEntity) -> User:
        """Convert domain entity to SQLAlchemy model."""
        model = User(
            email=entity.email,
            name=entity.name,
            password_hash=entity.password_hash,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            phone=entity.phone,
            role=entity.role,
            email_verified=entity.email_verified,
            phone_verified=entity.phone_verified,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, user: UserEntity) -> UserEntity:
        """Create a new user."""
        model = self._to_model(user)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: str) -> UserEntity | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[UserEntity]:
        """List all users (non-deleted)."""
        result = await self.session.execute(
            select(User).where(User.deleted_at.is_(None)).order_by(User.email)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, user: UserEntity) -> UserEntity:
        """Update a user."""
        result = await self.session.execute(select(User).where(User.id == user.id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User with id {user.id} not found")
        model.email = user.email
        model.name = user.name
        model.password_hash = user.password_hash
        model.updated_at = user.updated_at
        model.deleted_at = user.deleted_at
        model.phone = user.phone
        model.role = user.role
        model.email_verified = user.email_verified
        model.phone_verified = user.phone_verified
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)


class SQLAlchemyMembershipRepository(MembershipRepository):
    """SQLAlchemy implementation of MembershipRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Membership) -> MembershipEntity:
        """Convert SQLAlchemy model to domain entity."""
        return MembershipEntity(
            id=model.id,
            org_id=model.org_id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at,
            invited_email=model.invited_email,
            is_disabled=model.is_disabled,
            is_point_of_escalation=model.is_point_of_escalation,
            scheduling_priority=model.scheduling_priority,
            responsibility=model.responsibility,
            personalisation_notes=model.personalisation_notes,
        )

    def _to_model(self, entity: MembershipEntity) -> Membership:
        """Convert domain entity to SQLAlchemy model."""
        model = Membership(
            org_id=entity.org_id,
            user_id=entity.user_id,
            role=entity.role,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            invited_email=entity.invited_email,
            is_disabled=entity.is_disabled,
            is_point_of_escalation=entity.is_point_of_escalation,
            scheduling_priority=entity.scheduling_priority,
            responsibility=entity.responsibility,
            personalisation_notes=entity.personalisation_notes,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, membership: MembershipEntity) -> MembershipEntity:
        """Create a new membership."""
        model = self._to_model(membership)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_org_and_user(
        self, org_id: str, user_id: str
    ) -> MembershipEntity | None:
        """Get membership by org and user."""
        result = await self.session.execute(
            select(Membership).where(
                Membership.org_id == org_id,
                Membership.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_org_id(self, org_id: str) -> list[MembershipEntity]:
        """List memberships for an organization."""
        result = await self.session.execute(
            select(Membership)
            .where(Membership.org_id == org_id)
            .order_by(Membership.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, membership: MembershipEntity) -> MembershipEntity:
        """Update a membership."""
        result = await self.session.execute(
            select(Membership).where(Membership.id == membership.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Membership with id {membership.id} not found")
        model.role = membership.role
        model.updated_at = membership.updated_at
        model.user_id = membership.user_id
        model.invited_email = membership.invited_email
        model.is_disabled = membership.is_disabled
        model.is_point_of_escalation = membership.is_point_of_escalation
        model.scheduling_priority = membership.scheduling_priority
        model.responsibility = membership.responsibility
        model.personalisation_notes = membership.personalisation_notes
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, membership_id: str) -> None:
        """Delete a membership."""
        result = await self.session.execute(
            select(Membership).where(Membership.id == membership_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()


class SQLAlchemyMembershipUnavailabilityRepository(MembershipUnavailabilityRepository):
    """SQLAlchemy implementation of MembershipUnavailabilityRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: MembershipUnavailability) -> MembershipUnavailabilityEntity:
        """Convert SQLAlchemy model to domain entity."""
        return MembershipUnavailabilityEntity(
            id=model.id,
            member_id=model.member_id,
            start_date=model.start_date,
            end_date=model.end_date,
            start_time=model.start_time,
            end_time=model.end_time,
            recurrence_type=model.recurrence_type,
            days_of_week=model.days_of_week,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: MembershipUnavailabilityEntity) -> MembershipUnavailability:
        """Convert domain entity to SQLAlchemy model."""
        model = MembershipUnavailability(
            member_id=entity.member_id,
            start_date=entity.start_date,
            end_date=entity.end_date,
            start_time=entity.start_time,
            end_time=entity.end_time,
            recurrence_type=entity.recurrence_type,
            days_of_week=entity.days_of_week,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, unavailability: MembershipUnavailabilityEntity) -> MembershipUnavailabilityEntity:
        """Create a new membership unavailability."""
        model = self._to_model(unavailability)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, unavailability_id: str) -> MembershipUnavailabilityEntity | None:
        """Get unavailability by ID."""
        result = await self.session.execute(
            select(MembershipUnavailability).where(MembershipUnavailability.id == unavailability_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_member_id(self, member_id: str) -> list[MembershipUnavailabilityEntity]:
        """List unavailabilities for a membership."""
        result = await self.session.execute(
            select(MembershipUnavailability)
            .where(MembershipUnavailability.member_id == member_id)
            .order_by(MembershipUnavailability.start_date.desc().nullslast())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_org_id(self, org_id: str) -> list[MembershipUnavailabilityEntity]:
        """List unavailabilities for all members of an organization."""
        result = await self.session.execute(
            select(MembershipUnavailability)
            .join(Membership, MembershipUnavailability.member_id == Membership.id)
            .where(Membership.org_id == org_id)
            .order_by(MembershipUnavailability.start_date.desc().nullslast())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, unavailability: MembershipUnavailabilityEntity) -> MembershipUnavailabilityEntity:
        """Update a membership unavailability."""
        result = await self.session.execute(
            select(MembershipUnavailability).where(MembershipUnavailability.id == unavailability.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"MembershipUnavailability with id {unavailability.id} not found")
        model.start_date = unavailability.start_date
        model.end_date = unavailability.end_date
        model.start_time = unavailability.start_time
        model.end_time = unavailability.end_time
        model.recurrence_type = unavailability.recurrence_type
        model.days_of_week = unavailability.days_of_week
        model.updated_at = unavailability.updated_at
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, unavailability_id: str) -> None:
        """Delete a membership unavailability."""
        result = await self.session.execute(
            select(MembershipUnavailability).where(MembershipUnavailability.id == unavailability_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()


class SQLAlchemyLeadRepository(LeadRepository):
    """SQLAlchemy implementation of LeadRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Lead) -> LeadEntity:
        """Convert SQLAlchemy model to domain entity."""
        return LeadEntity(
            id=model.id,
            org_id=model.org_id,
            email=model.email,
            phone=model.phone,
            name=model.name,
            status=model.status,
            source=model.source,
            last_inquiry_date=model.last_inquiry_date,
            last_contact_date=model.last_contact_date,
            metadata=model.meta,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: LeadEntity) -> Lead:
        """Convert domain entity to SQLAlchemy model."""
        model = Lead(
            org_id=entity.org_id,
            email=entity.email,
            phone=entity.phone,
            name=entity.name,
            status=entity.status,
            source=entity.source,
            last_inquiry_date=entity.last_inquiry_date,
            last_contact_date=entity.last_contact_date,
            meta=entity.metadata,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, lead: LeadEntity) -> LeadEntity:
        """Create a new lead."""
        model = self._to_model(lead)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, lead_id: str) -> LeadEntity | None:
        """Get lead by ID."""
        result = await self.session.execute(
            select(Lead).where(
                Lead.id == lead_id,
                Lead.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, lead: LeadEntity) -> LeadEntity:
        """Update a lead."""
        result = await self.session.execute(select(Lead).where(Lead.id == lead.id))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Lead with id {lead.id} not found")
        model.email = lead.email
        model.phone = lead.phone
        model.name = lead.name
        model.status = lead.status
        model.source = lead.source
        model.last_inquiry_date = lead.last_inquiry_date
        model.last_contact_date = lead.last_contact_date
        model.meta = lead.metadata
        model.updated_at = lead.updated_at
        model.deleted_at = lead.deleted_at
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_by_org_id(
        self,
        org_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LeadEntity]:
        """List leads for an organization."""
        q = (
            select(Lead)
            .where(Lead.org_id == org_id, Lead.deleted_at.is_(None))
            .order_by(Lead.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status is not None:
            q = q.where(Lead.status == status)
        result = await self.session.execute(q)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of NoteRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Note) -> NoteEntity:
        """Convert SQLAlchemy model to domain entity."""
        return NoteEntity(
            id=model.id,
            lead_id=model.lead_id,
            content=model.content,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: NoteEntity) -> Note:
        """Convert domain entity to SQLAlchemy model."""
        model = Note(
            lead_id=entity.lead_id,
            content=entity.content,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, note: NoteEntity) -> NoteEntity:
        """Create a new note."""
        model = self._to_model(note)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_lead_id(self, lead_id: str) -> list[NoteEntity]:
        """Get notes for a lead."""
        result = await self.session.execute(
            select(Note).where(Note.lead_id == lead_id).order_by(Note.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]


class SQLAlchemyActivityRepository(ActivityRepository):
    """SQLAlchemy implementation of ActivityRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Activity) -> ActivityEntity:
        """Convert SQLAlchemy model to domain entity."""
        return ActivityEntity(
            id=model.id,
            lead_id=model.lead_id,
            type=model.type,
            description=model.description,
            metadata=model.meta,
            created_at=model.created_at,
        )

    def _to_model(self, entity: ActivityEntity) -> Activity:
        """Convert domain entity to SQLAlchemy model."""
        model = Activity(
            lead_id=entity.lead_id,
            type=entity.type,
            description=entity.description,
            meta=entity.metadata,
            created_at=entity.created_at,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def create(self, activity: ActivityEntity) -> ActivityEntity:
        """Create a new activity."""
        model = self._to_model(activity)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_by_lead_id(self, lead_id: str) -> list[ActivityEntity]:
        """Get activities for a lead."""
        result = await self.session.execute(
            select(Activity)
            .where(Activity.lead_id == lead_id)
            .order_by(Activity.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]


class SelectedCalendarRepository(ABC):
    """Abstract repository for selected calendars."""

    @abstractmethod
    async def list_by_member_id(self, member_id: str) -> list[dict]:
        pass

    @abstractmethod
    async def list_by_org_id(self, org_id: str) -> list[dict]:
        pass

    @abstractmethod
    async def get_by_id(self, calendar_id: int) -> dict | None:
        pass

    @abstractmethod
    async def upsert(self, data: dict) -> dict:
        pass

    @abstractmethod
    async def set_default(self, calendar_id: int, member_id: str) -> bool:
        pass

    @abstractmethod
    async def delete(self, calendar_id: int) -> bool:
        pass

    @abstractmethod
    async def update_sync_token(self, calendar_id: int, token: str) -> None:
        pass


class SQLAlchemySelectedCalendarRepository(SelectedCalendarRepository):
    """SQLAlchemy implementation of SelectedCalendarRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_dict(self, model: SelectedCalendar) -> dict:
        return {
            "id": model.id,
            "org_id": model.org_id,
            "credential_id": model.credential_id,
            "calendar_id": model.calendar_id,
            "calendar_name": model.calendar_name,
            "integration": model.integration,
            "is_default": model.is_default,
            "is_active_for_conflict_check": model.is_active_for_conflict_check,
            "member_id": model.member_id,
            "channel_id": model.channel_id,
            "resource_id": model.resource_id,
            "channel_expiration": model.channel_expiration,
            "last_synced_at": model.last_synced_at,
            "next_async_token": model.next_async_token,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

    async def list_by_member_id(self, member_id: str) -> list[dict]:
        result = await self.session.execute(
            select(SelectedCalendar)
            .where(SelectedCalendar.member_id == member_id)
            .order_by(SelectedCalendar.is_default.desc())
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def list_by_org_id(self, org_id: str) -> list[dict]:
        result = await self.session.execute(
            select(SelectedCalendar)
            .where(SelectedCalendar.org_id == org_id)
            .order_by(SelectedCalendar.is_default.desc())
        )
        return [self._to_dict(m) for m in result.scalars().all()]

    async def get_by_id(self, calendar_id: int) -> dict | None:
        result = await self.session.execute(
            select(SelectedCalendar).where(SelectedCalendar.id == calendar_id)
        )
        model = result.scalar_one_or_none()
        return self._to_dict(model) if model else None

    async def upsert(self, data: dict) -> dict:
        # Try to find existing by (member_id, calendar_id) pair
        result = await self.session.execute(
            select(SelectedCalendar).where(
                SelectedCalendar.member_id == data["member_id"],
                SelectedCalendar.calendar_id == data.get("calendar_id"),
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            from ....db.database import utc_now_ms
            now = utc_now_ms()
            model = SelectedCalendar(
                org_id=data.get("org_id"),
                credential_id=data.get("credential_id"),
                calendar_id=data.get("calendar_id"),
                calendar_name=data.get("calendar_name"),
                integration=data.get("integration"),
                is_default=data.get("is_default", False),
                is_active_for_conflict_check=data.get(
                    "is_active_for_conflict_check", True
                ),
                member_id=data["member_id"],
                created_at=now,
                updated_at=now,
            )
            self.session.add(model)
        else:
            if "calendar_name" in data:
                model.calendar_name = data["calendar_name"]
            if "integration" in data:
                model.integration = data["integration"]
            if "is_default" in data:
                model.is_default = data["is_default"]
            if "is_active_for_conflict_check" in data:
                model.is_active_for_conflict_check = data[
                    "is_active_for_conflict_check"
                ]
            if "credential_id" in data:
                model.credential_id = data["credential_id"]
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_dict(model)

    async def set_default(self, calendar_id: int, member_id: str) -> bool:
        # Clear all defaults for this member first
        all_result = await self.session.execute(
            select(SelectedCalendar).where(SelectedCalendar.member_id == member_id)
        )
        for m in all_result.scalars().all():
            m.is_default = m.id == calendar_id
        await self.session.flush()
        return True

    async def delete(self, calendar_id: int) -> bool:
        result = await self.session.execute(
            delete(SelectedCalendar).where(SelectedCalendar.id == calendar_id)
        )
        await self.session.flush()
        return result.rowcount is not None and result.rowcount > 0

    async def update_sync_token(self, calendar_id: int, token: str) -> None:
        result = await self.session.execute(
            select(SelectedCalendar).where(SelectedCalendar.id == calendar_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.next_async_token = token
            await self.session.flush()
