"""Use case for updating an organization."""

from ...domain.organization.entity import Organization as OrganizationEntity
from ...infrastructure.database.repositories import OrganizationRepository
from ...db.database import utc_now_ms


def _validate_country(country: str | None) -> str | None:
    """Validate and normalize country to ISO 3166-1 alpha-2 (2-letter) code."""
    if not country or not country.strip():
        return None
    normalized = country.strip().upper()
    if len(normalized) != 2 or not normalized.isalpha():
        raise ValueError(
            "Country must be a 2-letter ISO 3166-1 alpha-2 code (e.g. JP, US, PL)"
        )
    return normalized


class UpdateOrganizationUseCase:
    """Use case for updating organization fields."""

    def __init__(self, org_repo: OrganizationRepository):
        self.org_repo = org_repo

    async def execute(
        self,
        org_id: str,
        *,
        name: str | None = None,
        time_zone: str | None = None,
        country: str | None = None,
        currency: str | None = None,
        settings: dict | None = None,
        stripe_plan: str | None = None,
        stripe_customer_id: str | None = None,
        default_schedule_id: int | None = None,
        public_scheduler_configurations: dict | None = None,
        tag: str | None = None,
        seats: int | None = None,
        addons: dict | None = None,
    ) -> OrganizationEntity:
        """Update organization by ID. Only provided fields are updated."""
        organization = await self.org_repo.get_by_id(org_id)
        if not organization:
            raise ValueError(f"Organization {org_id} not found")

        now = utc_now_ms()
        if name is not None:
            organization.name = name
        if time_zone is not None:
            organization.time_zone = time_zone
        if country is not None:
            organization.country = _validate_country(country)
        if currency is not None:
            organization.currency = currency
        if settings is not None:
            organization.settings = settings
        if stripe_plan is not None:
            organization.stripe_plan = stripe_plan
        if stripe_customer_id is not None:
            organization.stripe_customer_id = stripe_customer_id
        if default_schedule_id is not None:
            organization.default_schedule_id = default_schedule_id
        if public_scheduler_configurations is not None:
            organization.public_scheduler_configurations = public_scheduler_configurations
        if tag is not None:
            organization.tag = tag
        if seats is not None:
            organization.seats = seats
        if addons is not None:
            organization.addons = addons

        organization.updated_at = now
        return await self.org_repo.update(organization)
