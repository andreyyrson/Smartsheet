from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api._filters import apply_action_filters, project_consultor_analista
from app.api._normalization import (
    CANONICAL_PROJECTS,
    aggregate_by_canonical,
)
from app.database import get_db
from app.models import Action
from app.people import list_analistas, list_estrategistas
from app.schemas import (
    BreakdownRow,
    ChartItem,
    DashboardCharts,
    DashboardSummary,
    FilterOptions,
)

router = APIRouter(tags=["dashboard"])


def _count(session: Session, stmt) -> int:
    return session.execute(stmt).scalar() or 0


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    projeto: str | None = None,
    consultor: str | None = None,
    analista: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    session: Session = Depends(get_db),
) -> DashboardSummary:
    today = date.today()
    week_later = today + timedelta(days=7)

    def base():
        return apply_action_filters(
            select(func.count()).select_from(Action),
            session,
            projeto=projeto,
            consultor=consultor,
            analista=analista,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    project_stmt = apply_action_filters(
        select(func.count(func.distinct(Action.department))).select_from(Action),
        session,
        projeto=projeto,
        consultor=consultor,
        analista=analista,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    total_projects = _count(session, project_stmt)

    total = _count(session, base())
    completed = _count(session, base().where(Action.is_completed.is_(True)))
    in_progress = _count(
        session,
        base()
        .where(Action.is_completed.is_(False))
        .where((Action.due_date.is_(None)) | (Action.due_date >= today)),
    )
    delayed = _count(
        session,
        base().where(Action.is_completed.is_(False)).where(Action.due_date < today),
    )
    blocked = _count(
        session,
        base().where(
            Action.status.ilike("%bloquead%") | Action.status.ilike("%blocked%")
        ),
    )
    critical = _count(
        session,
        base()
        .where(Action.is_completed.is_(False))
        .where((Action.due_date < today) | (Action.due_date <= week_later)),
    )
    due_soon = _count(
        session,
        base()
        .where(Action.is_completed.is_(False))
        .where(Action.due_date <= week_later)
        .where(Action.due_date >= today),
    )
    overdue = _count(
        session,
        base().where(Action.is_completed.is_(False)).where(Action.due_date < today),
    )

    completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0

    return DashboardSummary(
        total_projects=total_projects,
        total_actions=total,
        completed=completed,
        in_progress=in_progress,
        delayed=delayed,
        blocked=blocked,
        critical=critical,
        completion_rate=completion_rate,
        due_soon=due_soon,
        overdue=overdue,
    )


@router.get("/dashboard/charts", response_model=DashboardCharts)
def get_dashboard_charts(
    projeto: str | None = None,
    consultor: str | None = None,
    analista: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    session: Session = Depends(get_db),
) -> DashboardCharts:
    today = date.today()
    week_later = today + timedelta(days=7)

    def filtered(stmt):
        return apply_action_filters(
            stmt,
            session,
            projeto=projeto,
            consultor=consultor,
            analista=analista,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    # Calcular status baseados em lógica de negócio
    completed = _count(session, filtered(select(func.count()).select_from(Action).where(Action.is_completed.is_(True))))
    in_progress = _count(
        session,
        filtered(
            select(func.count()).select_from(Action)
            .where(Action.is_completed.is_(False))
            .where((Action.due_date.is_(None)) | (Action.due_date >= today))
        )
    )
    delayed = _count(
        session,
        filtered(
            select(func.count()).select_from(Action)
            .where(Action.is_completed.is_(False))
            .where(Action.due_date < today)
        )
    )
    critical = _count(
        session,
        filtered(
            select(func.count()).select_from(Action)
            .where(Action.is_completed.is_(False))
            .where((Action.due_date < today) | (Action.due_date <= week_later))
        )
    )
    due_soon = _count(
        session,
        filtered(
            select(func.count()).select_from(Action)
            .where(Action.is_completed.is_(False))
            .where(Action.due_date <= week_later)
            .where(Action.due_date >= today)
        )
    )

    actions_by_status = [
        ChartItem(label="Concluído", value=completed),
        ChartItem(label="Em andamento", value=in_progress),
        ChartItem(label="Atraso", value=delayed),
        ChartItem(label="Críticas", value=critical),
        ChartItem(label="Vencendo", value=due_soon),
    ]

    project_rows = session.execute(
        filtered(
            select(Action.department, func.count())
            .select_from(Action)
            .group_by(Action.department)
        )
    ).all()
    project_aggr = aggregate_by_canonical(project_rows)
    actions_by_project = [
        ChartItem(label=p, value=c)
        for p, c in sorted(project_aggr.items(), key=lambda r: r[1], reverse=True)
    ]

    today = date.today()
    in_progress_rows = session.execute(
        filtered(
            select(Action.department, func.count())
            .select_from(Action)
            .where(Action.is_completed.is_(False))
            .where((Action.due_date.is_(None)) | (Action.due_date >= today))
            .group_by(Action.department)
        )
    ).all()
    in_progress_aggr = aggregate_by_canonical(in_progress_rows)
    in_progress_by_project = [
        ChartItem(label=p, value=c)
        for p, c in sorted(in_progress_aggr.items(), key=lambda r: r[1], reverse=True)
    ]

    small_projects_alert = [
        ChartItem(label=p, value=c)
        for p, c in sorted(project_aggr.items(), key=lambda r: r[1])
        if c < 50
    ]

    return DashboardCharts(
        actions_by_status=actions_by_status,
        actions_by_project=actions_by_project,
        in_progress_by_project=in_progress_by_project,
        small_projects_alert=small_projects_alert,
    )


@router.get("/dashboard/breakdown", response_model=list[BreakdownRow])
def get_dashboard_breakdown(
    projeto: str | None = None,
    consultor: str | None = None,
    analista: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    session: Session = Depends(get_db),
) -> list[BreakdownRow]:
    today = date.today()
    proj_map = project_consultor_analista(session)

    def filtered(stmt):
        return apply_action_filters(
            stmt,
            session,
            projeto=projeto,
            consultor=consultor,
            analista=analista,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    rows = session.execute(
        filtered(
            select(Action.department, func.count())
            .select_from(Action)
            .group_by(Action.department)
        )
    ).all()

    result: list[BreakdownRow] = []
    for department, total in rows:
        completed = _count(
            session,
            filtered(select(func.count()).select_from(Action))
            .where(Action.department == department)
            .where(Action.is_completed.is_(True)),
        )
        in_progress = _count(
            session,
            filtered(select(func.count()).select_from(Action))
            .where(Action.department == department)
            .where(Action.is_completed.is_(False))
            .where((Action.due_date.is_(None)) | (Action.due_date >= today)),
        )
        overdue = _count(
            session,
            filtered(select(func.count()).select_from(Action))
            .where(Action.department == department)
            .where(Action.is_completed.is_(False))
            .where(Action.due_date < today),
        )
        cons, anal = proj_map.get(department, (None, None))
        completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0
        result.append(
            BreakdownRow(
                project=department or "Sem projeto",
                consultor=cons,
                analista=anal,
                total=total,
                completed=completed,
                in_progress=in_progress,
                overdue=overdue,
                completion_rate=completion_rate,
            )
        )

    result.sort(key=lambda r: r.total, reverse=True)
    return result


@router.get("/filters/options", response_model=FilterOptions)
def get_filter_options(session: Session = Depends(get_db)) -> FilterOptions:
    # Retorna todos os nomes canônicos informados, independente de terem dados
    projetos = sorted(CANONICAL_PROJECTS)
    status_list = [
        s
        for s in session.execute(
            select(Action.status).where(Action.status.isnot(None)).distinct()
        ).scalars()
        if s
    ]
    return FilterOptions(
        projetos=sorted(projetos),
        consultores=list_estrategistas(),
        analistas=list_analistas(),
        status=sorted(status_list),
    )
