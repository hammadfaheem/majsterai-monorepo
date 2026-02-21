"""Invoice routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms, generate_uuid
from ...domain.invoice.entity import Invoice as InvoiceEntity
from ...infrastructure.database.repositories import (
    InvoiceRepository,
    SQLAlchemyInvoiceRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> InvoiceRepository:
    return SQLAlchemyInvoiceRepository(db)


class InvoiceCreate(BaseModel):
    org_id: str
    lead_id: str | None = None
    status: str = "draft"
    date: int | None = None
    due_date: int | None = None
    tax_type: str | None = None
    reference: str | None = None
    notes: str | None = None


class InvoiceUpdate(BaseModel):
    status: str | None = None
    date: int | None = None
    due_date: int | None = None
    tax_type: str | None = None
    reference: str | None = None
    notes: str | None = None


class InvoiceResponse(BaseModel):
    id: str
    org_id: str
    lead_id: str | None
    index: int | None
    status: str
    date: int | None
    due_date: int | None
    tax_type: str | None
    reference: str | None
    notes: str | None
    accept_credit_card: bool
    reminder_sent: bool
    approved_at: int | None
    sent_at: int | None
    external_id: str | None
    last_synced_at: int | None
    is_sync_failed: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    org_id: str = Query(..., description="Organization ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: InvoiceRepository = Depends(get_repo),
):
    items = await repo.list_by_org_id(org_id, limit=limit, offset=offset)
    return [
        InvoiceResponse(
            id=i.id,
            org_id=i.org_id,
            lead_id=i.lead_id,
            index=i.index,
            status=i.status,
            date=i.date,
            due_date=i.due_date,
            tax_type=i.tax_type,
            reference=i.reference,
            notes=i.notes,
            accept_credit_card=i.accept_credit_card,
            reminder_sent=i.reminder_sent,
            approved_at=i.approved_at,
            sent_at=i.sent_at,
            external_id=i.external_id,
            last_synced_at=i.last_synced_at,
            is_sync_failed=i.is_sync_failed,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in items
    ]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str, repo: InvoiceRepository = Depends(get_repo)):
    i = await repo.get_by_id(invoice_id)
    if not i:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse(
        id=i.id,
        org_id=i.org_id,
        lead_id=i.lead_id,
        index=i.index,
        status=i.status,
        date=i.date,
        due_date=i.due_date,
        tax_type=i.tax_type,
        reference=i.reference,
        notes=i.notes,
        accept_credit_card=i.accept_credit_card,
        reminder_sent=i.reminder_sent,
        approved_at=i.approved_at,
        sent_at=i.sent_at,
        external_id=i.external_id,
        last_synced_at=i.last_synced_at,
        is_sync_failed=i.is_sync_failed,
        created_at=i.created_at,
        updated_at=i.updated_at,
    )


@router.post("/", response_model=InvoiceResponse)
async def create_invoice(data: InvoiceCreate, repo: InvoiceRepository = Depends(get_repo)):
    now = utc_now_ms()
    entity = InvoiceEntity(
        id=generate_uuid(),
        org_id=data.org_id,
        lead_id=data.lead_id,
        index=None,
        status=data.status,
        date=data.date,
        due_date=data.due_date,
        tax_type=data.tax_type,
        reference=data.reference,
        notes=data.notes,
        accept_credit_card=True,
        reminder_sent=False,
        approved_at=None,
        sent_at=None,
        external_id=None,
        last_synced_at=None,
        is_sync_failed=False,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return InvoiceResponse(
        id=created.id,
        org_id=created.org_id,
        lead_id=created.lead_id,
        index=created.index,
        status=created.status,
        date=created.date,
        due_date=created.due_date,
        tax_type=created.tax_type,
        reference=created.reference,
        notes=created.notes,
        accept_credit_card=created.accept_credit_card,
        reminder_sent=created.reminder_sent,
        approved_at=created.approved_at,
        sent_at=created.sent_at,
        external_id=created.external_id,
        last_synced_at=created.last_synced_at,
        is_sync_failed=created.is_sync_failed,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(invoice_id: str, data: InvoiceUpdate, repo: InvoiceRepository = Depends(get_repo)):
    existing = await repo.get_by_id(invoice_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    now = utc_now_ms()
    if data.status is not None:
        existing.status = data.status
    if data.date is not None:
        existing.date = data.date
    if data.due_date is not None:
        existing.due_date = data.due_date
    if data.tax_type is not None:
        existing.tax_type = data.tax_type
    if data.reference is not None:
        existing.reference = data.reference
    if data.notes is not None:
        existing.notes = data.notes
    existing.updated_at = now
    updated = await repo.update(existing)
    return InvoiceResponse(
        id=updated.id,
        org_id=updated.org_id,
        lead_id=updated.lead_id,
        index=updated.index,
        status=updated.status,
        date=updated.date,
        due_date=updated.due_date,
        tax_type=updated.tax_type,
        reference=updated.reference,
        notes=updated.notes,
        accept_credit_card=updated.accept_credit_card,
        reminder_sent=updated.reminder_sent,
        approved_at=updated.approved_at,
        sent_at=updated.sent_at,
        external_id=updated.external_id,
        last_synced_at=updated.last_synced_at,
        is_sync_failed=updated.is_sync_failed,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str, repo: InvoiceRepository = Depends(get_repo)):
    existing = await repo.get_by_id(invoice_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")
    await repo.delete(invoice_id)
    return {"message": "Deleted"}
