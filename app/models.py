# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    id      = Column(Integer, primary_key=True)
    name    = Column(String(120), unique=True, nullable=False)

class Note(Base):
    __tablename__ = "notes"
    id          = Column(Integer, primary_key=True)
    project_id  = Column(Integer, ForeignKey("projects.id"))
    author      = Column(String(80))
    body        = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", backref="notes")

class Forecast(Base):
    __tablename__ = "forecasts"
    id          = Column(Integer, primary_key=True)
    project_id  = Column(Integer, ForeignKey("projects.id"))
    horizon     = Column(Integer)          # days ahead
    value       = Column(Float)
    created_at  = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", backref="forecasts")