import re
import uuid
from datetime import date as date_cls
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Action, ActionHistory, Sheet, SyncRun
from app.smartsheet_client import smartsheet_client


# Mapeamento por nome de coluna (case-insensitive, sem acentos básicos)
COLUMN_MAP = {
    "atividade": "title",
    "status": "status",
    "responsável": "owner",
    "responsavel": "owner",
    "prazo": "due_date",
    "concluído": "is_completed",
    "concluido": "is_completed",
    "luz": "priority",
    "prioridade": "priority",
    "descrição": "description",
    "descricao": "description",
    "departamento": "department",
    "início": "start_date",
    "inicio": "start_date",
    "progresso": "progress",
    "% concluído": "progress",
    "% concluido": "progress",
}


def normalize(text: str | None) -> str:
    if not text:
        return ""
    return (
        text.lower()
        .strip()
        .replace("ã", "a")
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def build_column_mapping(columns: list[dict[str, Any]]) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for col in columns:
        normalized = normalize(col.get("title"))
        if normalized in COLUMN_MAP:
            mapping[COLUMN_MAP[normalized]] = col["id"]
    return mapping


def _get_cell_value(cells: list[dict[str, Any]], column_id: Any) -> Any:
    if column_id is None:
        return None
    for cell in cells:
        if cell.get("columnId") == column_id:
            return cell.get("value") or cell.get("displayValue")
    return None


def _parse_date(value: Any) -> date_cls | None:
    if not value:
        return None
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            except ValueError:
                return None
    return None


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "yes", "sim", "1", "concluído", "concluido")
    return False


def _extract_contact(value: Any) -> str | None:
    if isinstance(value, dict):
        return value.get("name") or value.get("email")
    if isinstance(value, str):
        return value
    return None


def _upsert_action(
    session: Session,
    sheet_id: uuid.UUID,
    sheet_name: str,
    row: dict[str, Any],
    mapping: dict[str, Any],
    run: SyncRun,
) -> bool:
    cells = row.get("cells", [])
    row_id = row["id"]

    title = _get_cell_value(cells, mapping.get("title"))
    status = _get_cell_value(cells, mapping.get("status"))
    owner = _extract_contact(_get_cell_value(cells, mapping.get("owner")))
    due_date = _parse_date(_get_cell_value(cells, mapping.get("due_date")))
    is_completed = _parse_bool(_get_cell_value(cells, mapping.get("is_completed")))
    priority = _get_cell_value(cells, mapping.get("priority"))
    description = _get_cell_value(cells, mapping.get("description"))
    start_date = _parse_date(_get_cell_value(cells, mapping.get("start_date")))
    progress = _get_cell_value(cells, mapping.get("progress"))

    extra_data: dict[str, Any] = {}
    for col_id, col_title in mapping.get("_reverse", {}).items():
        if col_title not in COLUMN_MAP:
            extra_data[col_title] = _get_cell_value(cells, int(col_id))

    progress_value = None
    if is_completed:
        progress_value = 100.0
    elif progress is not None:
        try:
            progress_value = float(progress)
        except (ValueError, TypeError):
            progress_value = None

    existing = session.execute(
        select(Action).where(
            Action.sheet_id == sheet_id, Action.smartsheet_row_id == row_id
        )
    ).scalar_one_or_none()

    if existing:
        changed = False
        fields = [
            ("title", title),
            ("status", status),
            ("owner", owner),
            ("due_date", due_date),
            ("is_completed", is_completed),
            ("priority", priority),
            ("description", description),
            ("start_date", start_date),
            ("progress", progress_value),
        ]
        for field_name, new_value in fields:
            old_value = getattr(existing, field_name)
            if old_value != new_value:
                setattr(existing, field_name, new_value)
                changed = True
                session.add(
                    ActionHistory(
                        action_id=existing.id,
                        field_name=field_name,
                        old_value=str(old_value) if old_value is not None else None,
                        new_value=str(new_value) if new_value is not None else None,
                    )
                )
        if extra_data:
            existing.extra_data = extra_data
        if changed:
            existing.updated_at = datetime.now(timezone.utc)
            run.rows_changed += 1
        return changed

    new_action = Action(
        sheet_id=sheet_id,
        smartsheet_row_id=row_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        owner=owner,
        owner_email=None,
        department=sheet_name,
        start_date=start_date,
        due_date=due_date,
        progress=progress_value,
        is_completed=is_completed,
        extra_data=extra_data,
    )
    session.add(new_action)
    run.rows_changed += 1
    return True


async def sync_sheet(sheet_id: int, full: bool = False) -> dict[str, Any]:
    run_id = uuid.uuid4()
    run = SyncRun(
        id=run_id,
        started_at=datetime.now(timezone.utc),
        status="running",
    )

    # Etapa 1: carregar/criar sheet e registrar o SyncRun
    with SessionLocal() as session:
        sheet = session.execute(
            select(Sheet).where(Sheet.smartsheet_id == sheet_id)
        ).scalar_one_or_none()

        if sheet is None:
            sheet_data = await smartsheet_client.get_sheet(sheet_id)
            sheet = Sheet(
                smartsheet_id=sheet_id,
                name=sheet_data.get("name", "Unknown"),
                permalink=sheet_data.get("permalink"),
                access_level=sheet_data.get("accessLevel"),
                sync_enabled=True,
            )
            session.add(sheet)
            session.commit()
            session.refresh(sheet)

        run.sheet_id = sheet.id
        sheet_id_uuid = sheet.id
        sheet_name = sheet.name
        last_sync_at = sheet.last_sync_at
        session.add(run)
        session.commit()

    # Etapa 2: chamar API externa fora de qualquer session
    modified_since = None
    if not full and last_sync_at:
        modified_since = last_sync_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    sheet_data = await smartsheet_client.get_sheet(sheet_id, modified_since)
    columns = sheet_data.get("columns", [])
    mapping = build_column_mapping(columns)
    mapping["_reverse"] = {str(col["id"]): col["title"] for col in columns}

    # Etapa 3: salvar dados em uma única session
    try:
        with SessionLocal() as session:
            db_sheet = session.get(Sheet, sheet_id_uuid)
            if db_sheet is None:
                raise RuntimeError("Sheet not found in database")
            db_sheet.column_mapping = mapping

            db_run = session.get(SyncRun, run_id)
            if db_run is None:
                raise RuntimeError("SyncRun not found in database")

            rows = sheet_data.get("rows", [])
            db_run.rows_processed = len(rows)
            for row in rows:
                _upsert_action(session, sheet_id_uuid, sheet_name, row, mapping, db_run)

            db_sheet.last_sync_at = datetime.now(timezone.utc)
            db_run.finished_at = datetime.now(timezone.utc)
            db_run.status = "success"
            session.commit()
            result = {
                "id": db_run.id,
                "status": db_run.status,
                "rows_processed": db_run.rows_processed,
                "rows_changed": db_run.rows_changed,
                "finished_at": db_run.finished_at,
            }
    except Exception as exc:
        with SessionLocal() as session:
            db_run = session.get(SyncRun, run_id)
            if db_run:
                db_run.finished_at = datetime.now(timezone.utc)
                db_run.status = "failed"
                db_run.error_message = str(exc)
                session.commit()
        raise

    return result


def is_action_sheet(name: str) -> bool:
    n = name.lower()
    return normalize(name).startswith("plano de acao") or "plano de ação" in n


def is_in_scope(name: str) -> bool:
    """Define se a planilha entra no escopo de sincronização:
    - é um 'Plano de Ação';
    - NÃO começa com '(Inativo)';
    - NÃO contém apenas anos <= 2024 (mantém 2025/2026 ou sem ano).
    """
    if not is_action_sheet(name):
        return False
    if normalize(name).startswith("(inativo)"):
        return False
    years = re.findall(r"20\d\d", name)
    if years and not any(y in ("2025", "2026") for y in years):
        return False
    return True


async def discover_action_sheets(session: Session) -> list[Sheet]:
    sheets = await smartsheet_client.list_sheets()
    created_or_updated: list[Sheet] = []

    for sheet_data in sheets:
        name = sheet_data.get("name", "")
        if is_action_sheet(name):
            smartsheet_id = sheet_data["id"]
            in_scope = is_in_scope(name)
            existing = session.execute(
                select(Sheet).where(Sheet.smartsheet_id == smartsheet_id)
            ).scalar_one_or_none()
            if existing is None:
                sheet = Sheet(
                    smartsheet_id=smartsheet_id,
                    name=name,
                    permalink=sheet_data.get("permalink"),
                    access_level=sheet_data.get("accessLevel"),
                    sync_enabled=in_scope,
                )
                session.add(sheet)
                created_or_updated.append(sheet)
            else:
                existing.name = name
                existing.permalink = sheet_data.get("permalink")
                existing.access_level = sheet_data.get("accessLevel")
                if in_scope:
                    existing.sync_enabled = True
                created_or_updated.append(existing)

    session.commit()
    for sheet in created_or_updated:
        session.refresh(sheet)
    return created_or_updated


async def sync_all_enabled(full: bool = True) -> dict[str, Any]:
    """Sincroniza sequencialmente todas as planilhas habilitadas, tolerante a
    erros por planilha."""
    with SessionLocal() as session:
        enabled = (
            session.execute(select(Sheet).where(Sheet.sync_enabled.is_(True)))
            .scalars()
            .all()
        )
        targets = [(s.smartsheet_id, s.name) for s in enabled]

    succeeded = 0
    failed = 0
    errors: list[dict[str, str]] = []
    for smartsheet_id, name in targets:
        try:
            await sync_sheet(smartsheet_id, full=full)
            succeeded += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"sheet": name, "error": str(exc)[:300]})

    return {
        "total": len(targets),
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors[:50],
    }
