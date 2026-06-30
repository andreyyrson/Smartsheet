from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Action
from app.schemas import ActionListResponse, ActionRead

router = APIRouter(tags=["actions"])


@router.get("/actions", response_model=ActionListResponse)
def list_actions(
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
    department: str | None = None,
    sheet_id: UUID | None = None,
    due_date_from: date | None = None,
    due_date_to: date | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db),
) -> ActionListResponse:
    stmt = select(func.count()).select_from(Action)
    filters = []
    if status:
        filters.append(Action.status.ilike(f"%{status}%"))
    if priority:
        filters.append(Action.priority.ilike(f"%{priority}%"))
    if owner:
        filters.append(Action.owner.ilike(f"%{owner}%"))
    if department:
        filters.append(Action.department.ilike(f"%{department}%"))
    if sheet_id:
        filters.append(Action.sheet_id == sheet_id)
    if due_date_from:
        filters.append(Action.due_date >= due_date_from)
    if due_date_to:
        filters.append(Action.due_date <= due_date_to)
    if search:
        filters.append(
            Action.title.ilike(f"%{search}%")
            | Action.owner.ilike(f"%{search}%")
            | Action.department.ilike(f"%{search}%")
        )
    if filters:
        stmt = stmt.where(*filters)

    total = session.execute(stmt).scalar() or 0

    stmt = select(Action)
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset(offset).limit(limit).order_by(Action.due_date.asc())
    items = session.execute(stmt).scalars().all()

    return ActionListResponse(
        total=total, items=[ActionRead.model_validate(a) for a in items]
    )


@router.get("/actions/{action_id}", response_model=ActionRead)
def get_action(action_id: UUID, session: Session = Depends(get_db)) -> ActionRead:
    action = session.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")
    return ActionRead.model_validate(action)
