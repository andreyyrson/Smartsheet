from datetime import date

from app.api.dashboard import get_dashboard_summary
from app.models import Action, Sheet


def test_dashboard_summary(db_session):
    sheet = Sheet(smartsheet_id=123, name="Test Sheet")
    db_session.add(sheet)
    db_session.commit()
    db_session.refresh(sheet)

    actions = [
        Action(
            sheet_id=sheet.id,
            smartsheet_row_id=1,
            title="A1",
            department="Test Sheet",
            is_completed=True,
        ),
        Action(
            sheet_id=sheet.id,
            smartsheet_row_id=2,
            title="A2",
            department="Test Sheet",
            is_completed=False,
            due_date=date(2020, 1, 1),
        ),
        Action(
            sheet_id=sheet.id,
            smartsheet_row_id=3,
            title="A3",
            department="Test Sheet",
            is_completed=False,
            due_date=date(2099, 12, 31),
        ),
    ]
    db_session.add_all(actions)
    db_session.commit()

    summary = get_dashboard_summary(session=db_session)
    assert summary.total_projects == 1
    assert summary.total_actions == 3
    assert summary.completed == 1
    assert summary.overdue == 1
    assert summary.due_soon == 0
    assert summary.completion_rate == 33.33
