# app/main.py
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text

from app.models import Note                     # ← SQLAlchemy model

# ────────────────────────────────────
#  Pydantic request / response models
# ────────────────────────────────────
class NoteIn(BaseModel):
    project_id: int
    author: str
    body: str


class NoteOut(NoteIn):
    id: int
    created_at: datetime                       # MUST be datetime

    # Pydantic-v2: tells the model to read attrs from ORM objects
    model_config = ConfigDict(from_attributes=True)

# ──────────────────────────────
#  DB setup  (SQLite for now)
# ──────────────────────────────
DB_URL = "sqlite:///company.db"
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)


from typing import Generator

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──────────────────────────────
#  FastAPI app + endpoints
# ──────────────────────────────
app = FastAPI(title="LLM-Demo FOR WORK")


@app.get("/notes", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db)):
    rows = (
        db.execute(select(Note).order_by(Note.id.desc()).limit(50))
        .scalars()
        .all()
    )
    return rows


@app.post("/notes", response_model=NoteOut)
def create_note(note: NoteIn, db: Session = Depends(get_db)):
    row = Note(**note.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.get("/real-estate", response_model=list[dict])
def real_estate(limit: int = 100, db: Session = Depends(get_db)):
    q = text("SELECT * FROM real_estate_mock LIMIT :n")
    rows = db.execute(q, {"n": limit})
    return [dict(r._mapping) for r in rows]    # ← changed line

# app/main.py
from llm import call_llm

@app.post("/forecast/cap_rate/{project_id}")
def cap_rate(project_id: str):
    payload = {
        "name": "get_cap_rate_forecast",
        "args_schema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"}
            },
            "required": ["project"]
        },
        "prompt": {
            "role": "user",
            "content": f"Forecast exit cap rates for {project_id}"
        }
    }
    return call_llm(payload)