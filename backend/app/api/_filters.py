"""Helpers de filtragem compartilhados pelos endpoints de dashboard."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api._normalization import CANONICAL_PROJECTS, normalize_project_name
from app.models import Action
from app.people import resolve_person


def distinct_owners(session: Session) -> list[str]:
    rows = session.execute(
        select(Action.owner).where(Action.owner.isnot(None)).distinct()
    ).scalars()
    return [o for o in rows if o]


def owners_resolving_to(session: Session, person: str) -> list[str]:
    """Valores brutos de `owner` que resolvem para a pessoa informada."""
    return [o for o in distinct_owners(session) if resolve_person(o) == person]


def project_consultor_analista(
    session: Session,
) -> dict[str, tuple[str | None, str | None]]:
    """Mapeia cada projeto (department) para (consultor, analista) inferidos a
    partir dos owners das ações daquele projeto. Pega o primeiro estrategista/
    analista encontrado por projeto."""
    from app.people import person_roles

    result: dict[str, tuple[str | None, str | None]] = {}
    rows = session.execute(
        select(Action.department, Action.owner).where(Action.department.isnot(None))
    ).all()
    acc: dict[str, list[str | None]] = {}
    for department, owner in rows:
        cons, anal = acc.get(department, [None, None])
        person = resolve_person(owner)
        if person:
            roles = person_roles(person)
            if "estrategista" in roles and cons is None:
                cons = person
            if "analista" in roles and anal is None:
                anal = person
        acc[department] = [cons, anal]
    for department, (cons, anal) in acc.items():
        result[department] = (cons, anal)
    return result


def distinct_departments(session: Session) -> list[str]:
    rows = session.execute(
        select(Action.department).where(Action.department.isnot(None)).distinct()
    ).scalars()
    return [d for d in rows if d]


def departments_for_canonical(session: Session, canonical: str) -> list[str]:
    """Retorna os departments brutos que normalizam para o nome canônico."""
    return [
        d
        for d in distinct_departments(session)
        if normalize_project_name(d) == canonical
    ]


def apply_action_filters(
    stmt,
    session: Session,
    *,
    projeto: str | None = None,
    consultor: str | None = None,
    analista: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    """Aplica os filtros comuns a uma query sobre Action.

    Quando `projeto` é um nome canônico, expande para todos os departments
    brutos que mapeiam para ele.

    Quando `status` é um status calculado, aplica a lógica correspondente."""
    if projeto:
        if projeto in CANONICAL_PROJECTS:
            depts = departments_for_canonical(session, projeto)
            stmt = stmt.where(
                Action.department.in_(depts) if depts else Action.id.is_(None)
            )
        else:
            stmt = stmt.where(Action.department == projeto)
    if status:
        today = date.today()
        week_later = today + timedelta(days=7)
        if status == "Concluído" or status == "Concluido":
            stmt = stmt.where(Action.is_completed.is_(True))
        elif status == "Em andamento":
            stmt = stmt.where(
                Action.is_completed.is_(False)
            ).where((Action.due_date.is_(None)) | (Action.due_date >= today))
        elif status == "Atraso":
            stmt = stmt.where(
                Action.is_completed.is_(False)
            ).where(Action.due_date < today)
        elif status == "Críticas" or status == "Criticas":
            stmt = stmt.where(
                Action.is_completed.is_(False)
            ).where(Action.due_date < today - timedelta(days=7))
        elif status == "Vencendo":
            stmt = stmt.where(
                Action.is_completed.is_(False)
            ).where(Action.due_date <= week_later).where(Action.due_date >= today)
        else:
            # Fallback para status brutos (caso não seja status calculado)
            stmt = stmt.where(Action.status.ilike(f"%{status}%"))
    if date_from:
        stmt = stmt.where(Action.due_date >= date_from)
    if date_to:
        stmt = stmt.where(Action.due_date <= date_to)
    if consultor:
        owners = owners_resolving_to(session, consultor)
        stmt = stmt.where(Action.owner.in_(owners) if owners else Action.id.is_(None))
    if analista:
        owners = owners_resolving_to(session, analista)
        stmt = stmt.where(Action.owner.in_(owners) if owners else Action.id.is_(None))
    return stmt
