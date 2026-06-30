from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Sheet
from app.schemas import SheetRead, SyncResult
from app.sync_service import discover_action_sheets, sync_all_enabled, sync_sheet

router = APIRouter(tags=["sheets"])


@router.get("/sheets", response_model=list[SheetRead])
def list_sheets(session: Session = Depends(get_db)) -> list[SheetRead]:
    sheets = session.execute(select(Sheet).order_by(Sheet.name)).scalars().all()
    return [SheetRead.model_validate(s) for s in sheets]


@router.post("/sheets/discover", response_model=list[SheetRead])
async def discover_sheets(session: Session = Depends(get_db)) -> list[SheetRead]:
    sheets = await discover_action_sheets(session)
    return [SheetRead.model_validate(s) for s in sheets]


@router.post("/sheets/sync-all")
async def sync_all_endpoint(full: bool = True) -> dict:
    return await sync_all_enabled(full=full)


@router.post("/sheets/{sheet_id}/sync", response_model=SyncResult)
async def sync_sheet_endpoint(
    sheet_id: UUID, full: bool = False, session: Session = Depends(get_db)
) -> SyncResult:
    sheet = session.get(Sheet, sheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")

    run = await sync_sheet(sheet.smartsheet_id, full=full)
    return SyncResult(
        sync_run_id=run["id"],
        status=run["status"],
        rows_processed=run["rows_processed"],
        rows_changed=run["rows_changed"],
        finished_at=run["finished_at"],
    )


@router.patch("/sheets/{sheet_id}/enable", response_model=SheetRead)
def enable_sheet(sheet_id: UUID, session: Session = Depends(get_db)) -> SheetRead:
    sheet = session.get(Sheet, sheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    sheet.sync_enabled = True
    session.commit()
    session.refresh(sheet)
    return SheetRead.model_validate(sheet)


@router.patch("/sheets/{sheet_id}/disable", response_model=SheetRead)
def disable_sheet(sheet_id: UUID, session: Session = Depends(get_db)) -> SheetRead:
    sheet = session.get(Sheet, sheet_id)
    if sheet is None:
        raise HTTPException(status_code=404, detail="Sheet not found")
    sheet.sync_enabled = False
    session.commit()
    session.refresh(sheet)
    return SheetRead.model_validate(sheet)
