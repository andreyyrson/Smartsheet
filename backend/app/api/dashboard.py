from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api._filters import apply_action_filters, project_consultor_analista
from app.api._normalization import (
    CANONICAL_PROJECTS,
    aggregate_by_canonical,
    normalize_project_name,
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
    critical = _count(
        session,
        base()
        .where(Action.is_completed.is_(False))
        .where(Action.due_date < today - timedelta(days=7)),
    )
    due_soon = _count(
        session,
        base()
        .where(Action.is_completed.is_(False))
        .where(Action.due_date <= week_later)
        .where(Action.due_date >= today),
    )

    completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0

    return DashboardSummary(
        total_projects=total_projects,
        total_actions=total,
        completed=completed,
        in_progress=in_progress,
        delayed=delayed,
        critical=critical,
        completion_rate=completion_rate,
        due_soon=due_soon,
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
            .where(Action.due_date < today - timedelta(days=7))
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

    # Agregar por projeto canônico
    project_totals: dict[str, int] = {}
    project_completed: dict[str, int] = {}
    project_in_progress: dict[str, int] = {}
    project_overdue: dict[str, int] = {}
    project_consultor: dict[str, str | None] = {}
    project_analista: dict[str, str | None] = {}

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
        normalized_project = normalize_project_name(department) or department or "Sem projeto"

        project_totals[normalized_project] = project_totals.get(normalized_project, 0) + total
        project_completed[normalized_project] = project_completed.get(normalized_project, 0) + completed
        project_in_progress[normalized_project] = project_in_progress.get(normalized_project, 0) + in_progress
        project_overdue[normalized_project] = project_overdue.get(normalized_project, 0) + overdue
        # Guardar o primeiro consultor/analista encontrado para o projeto canônico
        if normalized_project not in project_consultor and cons:
            project_consultor[normalized_project] = cons
        if normalized_project not in project_analista and anal:
            project_analista[normalized_project] = anal

    result: list[BreakdownRow] = []
    for project in project_totals:
        total = project_totals[project]
        completed = project_completed.get(project, 0)
        in_progress = project_in_progress.get(project, 0)
        overdue = project_overdue.get(project, 0)
        completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0
        result.append(
            BreakdownRow(
                project=project,
                consultor=project_consultor.get(project),
                analista=project_analista.get(project),
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
    # Status calculados usados no dashboard
    status_list = ["Concluído", "Em andamento", "Atraso", "Críticas", "Vencendo"]
    return FilterOptions(
        projetos=sorted(projetos),
        consultores=list_estrategistas(),
        analistas=list_analistas(),
        status=status_list,
    )
