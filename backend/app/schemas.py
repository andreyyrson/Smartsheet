from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActionRead(BaseModel):
    id: UUID
    sheet_id: UUID
    smartsheet_row_id: int
    title: str | None
    description: str | None
    status: str | None
    priority: str | None
    owner: str | None
    owner_email: str | None
    department: str | None
    start_date: date | None
    due_date: date | None
    progress: float | None
    is_completed: bool
    extra_data: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionListResponse(BaseModel):
    total: int
    items: list[ActionRead]


class DashboardSummary(BaseModel):
    total_projects: int
    total_actions: int
    completed: int
    in_progress: int
    delayed: int
    critical: int
    completion_rate: float
    due_soon: int


class ChartItem(BaseModel):
    label: str
    value: int


class DashboardCharts(BaseModel):
    actions_by_status: list[ChartItem]
    actions_by_project: list[ChartItem]
    in_progress_by_project: list[ChartItem]
    small_projects_alert: list[ChartItem]


class BreakdownRow(BaseModel):
    project: str
    consultor: str | None
    analista: str | None
    total: int
    completed: int
    in_progress: int
    overdue: int
    completion_rate: float


class FilterOptions(BaseModel):
    projetos: list[str]
    consultores: list[str]
    analistas: list[str]
    status: list[str]


class SheetRead(BaseModel):
    id: UUID
    smartsheet_id: int
    name: str
    permalink: str | None
    access_level: str | None
    sync_enabled: bool
    last_sync_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncResult(BaseModel):
    sync_run_id: UUID
    status: str
    rows_processed: int
    rows_changed: int
    finished_at: datetime | None
