# app/db.py
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DB_URL = "sqlite:///company.db"
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)

def get_company_db() -> Session:   # ← just a generator function
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()