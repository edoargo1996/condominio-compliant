from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .db import engine, init_db
from .models import Building, BuildingDeadline, DeadlineType, Administrator
from .services import onboarding_building, refresh_statuses

app = FastAPI(title="Condominio Compliant")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    with Session(engine) as session:
        refresh_statuses(session)
        buildings = session.exec(select(Building)).all()
        rows = []
        for b in buildings:
            admin = session.get(Administrator, b.administrator_id)
            deadlines = session.exec(select(BuildingDeadline).where(BuildingDeadline.building_id == b.id)).all()
            for d in deadlines:
                dt = session.get(DeadlineType, d.deadline_type_id)
                days_left = (d.due_date - date.today()).days
                rows.append({
                    "building": b.name,
                    "city": b.city,
                    "admin": admin.email,
                    "deadline": dt.name,
                    "law": dt.legal_reference,
                    "due_date": d.due_date.isoformat(),
                    "status": d.status,
                    "days_left": days_left,
                })

    return templates.TemplateResponse("dashboard.html", {"request": request, "rows": rows})


@app.get("/onboarding", response_class=HTMLResponse)
def onboarding_form(request: Request):
    with Session(engine) as session:
        categories = sorted(set(session.exec(select(DeadlineType.category)).all()))
    return templates.TemplateResponse("onboarding.html", {"request": request, "categories": categories})


@app.post("/onboarding")
def onboarding_submit(
    admin_name: str = Form(...),
    admin_email: str = Form(...),
    admin_whatsapp: str = Form(""),
    building_name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    categories: list[str] = Form(...),
):
    with Session(engine) as session:
        onboarding_building(
            session=session,
            admin_name=admin_name,
            admin_email=admin_email,
            admin_whatsapp=admin_whatsapp or None,
            building_name=building_name,
            city=city,
            address=address,
            categories=categories,
        )
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/api/notifications/run")
def run_notifications():
    logs: list[str] = []
    with Session(engine) as session:
        refresh_statuses(session)
        deadlines = session.exec(select(BuildingDeadline)).all()
        for d in deadlines:
            dt = session.get(DeadlineType, d.deadline_type_id)
            building = session.get(Building, d.building_id)
            admin = session.get(Administrator, building.administrator_id)
            days_left = (d.due_date - date.today()).days
            remind_days = dt.reminder_days_before
            should_notify = d.due_date < date.today() or d.due_date <= date.today() + timedelta(days=remind_days)
            if should_notify:
                text = (
                    f"[{date.today().isoformat()}] NOTIFICA {admin.email}"
                    f" | {building.name} | {dt.name} | scadenza {d.due_date.isoformat()}"
                    f" | stato={d.status}"
                )
                logs.append(text)

    log_path = Path(__file__).resolve().parents[1] / "notifications.log"
    if logs:
        with log_path.open("a", encoding="utf-8") as f:
            for line in logs:
                f.write(line + "\n")

    return {"notifications": len(logs), "log_file": str(log_path), "preview": logs[:10]}
