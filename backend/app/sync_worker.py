import asyncio
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Sheet
from app.sync_service import discover_action_sheets, sync_sheet


async def run_full_sync() -> None:
    with SessionLocal() as session:
        await discover_action_sheets(session)
        sheets = (
            session.execute(select(Sheet).where(Sheet.sync_enabled.is_(True)))
            .scalars()
            .all()
        )
        for sheet in sheets:
            try:
                await sync_sheet(sheet.smartsheet_id, full=True)
            except Exception:
                # Log estruturado seria adicionado aqui
                pass


async def run_incremental_sync() -> None:
    with SessionLocal() as session:
        sheets = (
            session.execute(
                select(Sheet)
                .where(Sheet.sync_enabled.is_(True))
                .where(Sheet.last_sync_at.isnot(None))
            )
            .scalars()
            .all()
        )
        for sheet in sheets:
            try:
                await sync_sheet(sheet.smartsheet_id, full=False)
            except Exception:
                pass


async def main() -> None:
    scheduler = AsyncIOScheduler()

    # Full sync ao iniciar e depois a cada 24h
    scheduler.add_job(
        run_full_sync,
        "interval",
        hours=settings.FULL_SYNC_INTERVAL_HOURS,
        next_run_time=datetime.now(timezone.utc),
    )

    # Incremental sync a cada 15 min
    scheduler.add_job(
        run_incremental_sync,
        "interval",
        minutes=settings.SYNC_INTERVAL_MINUTES,
    )

    scheduler.start()
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
