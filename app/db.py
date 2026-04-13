from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine, select, func

DB_PATH = Path("/home/edoargo/.condominio-compliant/condominio.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    from .models import DeadlineType

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(func.count()).select_from(DeadlineType)).one()
        if existing == 0:
            seed_deadline_types(session)


def seed_deadline_types(session: Session) -> None:
    from .models import DeadlineType

    defaults = [
        DeadlineType(
            code="ASCENSORE_BIENNALE",
            name="Verifica ascensore biennale",
            legal_reference="DPR 162/1999",
            recurrence_months=24,
            reminder_days_before=60,
            category="ascensore",
        ),
        DeadlineType(
            code="CALDAIA_ANNUALE",
            name="Controllo efficienza caldaia",
            legal_reference="DPR 74/2013",
            recurrence_months=12,
            reminder_days_before=30,
            category="caldaia",
        ),
        DeadlineType(
            code="ANTINCENDIO_SEMESTRALE",
            name="Manutenzione antincendio",
            legal_reference="DPR 151/2011",
            recurrence_months=6,
            reminder_days_before=30,
            category="antincendio",
        ),
        DeadlineType(
            code="APE_DECENNALE",
            name="Aggiornamento APE",
            legal_reference="DLgs 192/2005",
            recurrence_months=120,
            reminder_days_before=120,
            category="ape",
        ),
        DeadlineType(
            code="ANAC_ANNUALE",
            name="Registro controlli ANAC",
            legal_reference="Legge 220/2012",
            recurrence_months=12,
            reminder_days_before=30,
            category="anac",
        ),
    ]
    for item in defaults:
        session.add(item)
    session.commit()
