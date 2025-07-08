from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from faker import Faker
import random, datetime as dt

from app.models import Base, Project, Note, Forecast

DB_URL = "sqlite:///company.db"        # later: swap for Postgres URL
engine = create_engine(DB_URL, future=True)

def main():
    fake = Faker()             # generates realistic names / sentences
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # ---- projects --------------------------------------------------
        projects = [Project(name=fake.bs().title()) for _ in range(10)]
        db.add_all(projects); db.flush()          # assigns IDs

        # ---- notes & forecasts -----------------------------------------
        today = dt.date.today()
        for p in projects:
            for _ in range(8):   # 8 notes each
                db.add(Note(
                    project_id=p.id,
                    author=fake.first_name(),
                    body=fake.text(max_nb_chars=120),
                    created_at=fake.date_time_this_year()))
            for d in range(30):  # 30-day horizon forecasts
                db.add(Forecast(
                    project_id=p.id,
                    horizon=d+1,
                    value=round(random.uniform(50, 150), 2),
                    created_at=today))
        db.commit()

if __name__ == "__main__":
    main()