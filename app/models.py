from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Administrator(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    whatsapp: Optional[str] = None


class Building(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    administrator_id: int = Field(foreign_key="administrator.id")
    name: str
    city: str
    address: str


class DeadlineType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    name: str
    legal_reference: str
    recurrence_months: int
    reminder_days_before: int = 30
    category: str = Field(index=True)


class BuildingDeadline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    building_id: int = Field(foreign_key="building.id")
    deadline_type_id: int = Field(foreign_key="deadlinetype.id")
    due_date: date
    last_completed_at: Optional[date] = None
    status: str = Field(default="ok", index=True)
