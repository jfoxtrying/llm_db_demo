from pathlib import Path
DB_PATH = Path(__file__).resolve().parent.parent / "company.db"
DB_URL  = f"sqlite:///{DB_PATH}"