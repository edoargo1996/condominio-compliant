from datetime import date, timedelta
from typing import Iterable

from sqlmodel import Session, select

from .models import Administrator, Building, BuildingDeadline, DeadlineType


def add_months(start: date, months: int) -> date:
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    day = min(start.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def status_for_due_date(due_date: date) -> str:
    today = date.today()
    if due_date < today:
        return "scaduto"
    if due_date <= today + timedelta(days=30):
        return "in_scadenza"
    return "ok"


def onboarding_building(
    session: Session,
    admin_name: str,
    admin_email: str,
    admin_whatsapp: str | None,
    building_name: str,
    city: str,
    address: str,
    categories: Iterable[str],
) -> Building:
    admin = Administrator(name=admin_name, email=admin_email, whatsapp=admin_whatsapp)
    session.add(admin)
    session.flush()

    building = Building(
        administrator_id=admin.id,
        name=building_name,
        city=city,
        address=address,
    )
    session.add(building)
    session.flush()

    deadline_types = session.exec(
        select(DeadlineType).where(DeadlineType.category.in_(list(categories)))
    ).all()

    today = date.today()
    for dt in deadline_types:
        due = add_months(today, dt.recurrence_months)
        session.add(
            BuildingDeadline(
                building_id=building.id,
                deadline_type_id=dt.id,
                due_date=due,
                status=status_for_due_date(due),
            )
        )

    session.commit()
    session.refresh(building)
    return building


def refresh_statuses(session: Session) -> int:
    deadlines = session.exec(select(BuildingDeadline)).all()
    updated = 0
    for d in deadlines:
        new = status_for_due_date(d.due_date)
        if d.status != new:
            d.status = new
            session.add(d)
            updated += 1
    session.commit()
    return updated
