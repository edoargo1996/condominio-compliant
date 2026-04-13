from datetime import date

from app.services import add_months, status_for_due_date


def test_add_months_handles_month_end():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_status_for_due_date():
    assert status_for_due_date(date.today()) == "in_scadenza"
