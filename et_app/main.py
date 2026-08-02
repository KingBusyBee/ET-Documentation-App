from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from datetime import datetime, date
from typing import List
import os
import uuid

from database import init_db, get_db, Session, MISSOURI_SUBJECTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Emergent Thought Documentation App")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

init_db()

# ── helpers ──────────────────────────────────────────────────────────────────

CORE_SUBJECTS = {"Reading", "Language Arts", "Mathematics", "Social Studies", "Science"}
ANNUAL_GOAL = 1000
CORE_GOAL = 600

def get_year_totals(db: DBSession, year: int):
    year_str = str(year)
    rows = (
        db.query(Session.subject, func.sum(Session.duration_minutes))
        .filter(Session.date.like(f"{year_str}-%"))
        .group_by(Session.subject)
        .all()
    )
    by_subject = {r[0]: round(r[1] / 60, 2) for r in rows}
    total_hours = sum(by_subject.values())
    core_hours = sum(v for k, v in by_subject.items() if k in CORE_SUBJECTS)
    return {
        "by_subject": by_subject,
        "total_hours": round(total_hours, 2),
        "core_hours": round(core_hours, 2),
        "total_pct": min(round((total_hours / ANNUAL_GOAL) * 100, 1), 100),
        "core_pct": min(round((core_hours / CORE_GOAL) * 100, 1), 100),
    }

def group_sessions_for_print(sessions):
    """
    Combines rows that were logged together (same log_group_id — e.g. one
    day's entry covering Math + Reading in a single submission) into one
    printable log line, so the compliance record reads as one entry per
    actual sitting rather than one row per subject.
    """
    groups = {}
    order = []
    for s in sessions:
        key = s.log_group_id or f"single-{s.id}"
        if key not in groups:
            groups[key] = {
                "date": s.date,
                "notes": s.notes,
                "log_items": [],
                "sort_key": (s.date, s.created_at or datetime.min),
            }
            order.append(key)
        groups[key]["log_items"].append({
            "subject": s.subject,
            "duration_minutes": s.duration_minutes,
        })
    entries = list(groups.values())
    entries.sort(key=lambda g: g["sort_key"])
    for g in entries:
        g["total_minutes"] = sum(i["duration_minutes"] for i in g["log_items"])
    return entries

# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: DBSession = Depends(get_db)):
    year = date.today().year
    totals = get_year_totals(db, year)
    recent = (
        db.query(Session)
        .order_by(Session.created_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse(request, "index.html", {
        "subjects": MISSOURI_SUBJECTS,
        "totals": totals,
        "recent": recent,
        "year": year,
        "annual_goal": ANNUAL_GOAL,
        "core_goal": CORE_GOAL,
        "today": date.today().isoformat(),
    })


@app.post("/log")
async def log_session(
    request: Request,
    session_date: str = Form(...),
    subjects: List[str] = Form(...),
    durations: List[float] = Form(...),
    notes: str = Form(""),
    db: DBSession = Depends(get_db),
):
    # subjects[i] pairs with durations[i]. Skip any row where duration is
    # blank/zero — this happens if a parent adds a row and then decides not
    # to fill it in, so we don't want an empty line item saved.
    pairs = [(subj, dur) for subj, dur in zip(subjects, durations) if dur and dur > 0]

    if not pairs:
        return RedirectResponse("/", status_code=303)

    # One shared id links every subject logged in this single submission,
    # so the print view can show "Math 30 min + Reading 20 min" as one entry
    # instead of two separate lines, while totals-by-subject still count
    # each subject's minutes correctly under the hood.
    group_id = str(uuid.uuid4()) if len(pairs) > 1 else None

    for subj, dur in pairs:
        db.add(Session(
            date=session_date,
            subject=subj,
            duration_minutes=round(dur, 1),
            notes=notes.strip(),
            log_group_id=group_id,
        ))
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.delete("/session/{session_id}")
async def delete_session(session_id: int, db: DBSession = Depends(get_db)):
    s = db.query(Session).filter(Session.id == session_id).first()
    if s:
        db.delete(s)
        db.commit()
    return JSONResponse({"ok": True})


@app.get("/api/totals")
async def api_totals(year: int = None, db: DBSession = Depends(get_db)):
    if year is None:
        year = date.today().year
    return get_year_totals(db, year)


@app.get("/print", response_class=HTMLResponse)
async def print_log(request: Request, year: int = None, db: DBSession = Depends(get_db)):
    if year is None:
        year = date.today().year
    sessions = (
        db.query(Session)
        .filter(Session.date.like(f"{year}-%"))
        .order_by(Session.date.asc(), Session.created_at.asc())
        .all()
    )
    totals = get_year_totals(db, year)
    entries = group_sessions_for_print(sessions)
    return templates.TemplateResponse(request, "print.html", {
        "entries": entries,
        "totals": totals,
        "year": year,
        "annual_goal": ANNUAL_GOAL,
        "core_goal": CORE_GOAL,
        "core_subjects": sorted(CORE_SUBJECTS),
        "generated_on": date.today().isoformat(),
    })


@app.get("/sessions", response_class=HTMLResponse)
async def all_sessions(request: Request, db: DBSession = Depends(get_db)):
    year = date.today().year
    sessions = db.query(Session).order_by(Session.date.desc(), Session.created_at.desc()).all()
    totals = get_year_totals(db, year)
    return templates.TemplateResponse(request, "sessions.html", {
        "sessions": sessions,
        "totals": totals,
        "year": year,
        "annual_goal": ANNUAL_GOAL,
        "core_goal": CORE_GOAL,
    })
