from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys


def get_data_dir():
    """
    Where the real database file lives.

    Running as a plain .py file: same folder as this file (unchanged behavior).

    Running as a packaged .exe (PyInstaller): the app is unpacked into a fresh
    temp folder every launch, so anything saved next to this file would be
    deleted the moment the app closes. Instead, store the .db file in the
    user's permanent AppData folder, so hours logged today are still there
    next time the app opens.
    """
    if getattr(sys, "frozen", False):
        app_data = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "EmergentThought",
        )
        os.makedirs(app_data, exist_ok=True)
        return app_data
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_data_dir()
DB_PATH = os.path.join(BASE_DIR, "et_docs.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

MISSOURI_SUBJECTS = [
    "Reading",
    "Language Arts",
    "Mathematics",
    "Social Studies",
    "Science",
    "Other / Elective",
]

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)          # ISO date string YYYY-MM-DD
    subject = Column(String, nullable=False)       # one of MISSOURI_SUBJECTS
    duration_minutes = Column(Float, nullable=False)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    # Rows created from the same form submission (e.g. "Math 30 min + Reading 20 min"
    # logged as one entry) share this id, so the print view can show them as one
    # combined log line instead of separate ones. Older single-subject rows have
    # this as NULL and are treated as their own standalone entry.
    log_group_id = Column(String, nullable=True, index=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_add_log_group_id()

def _migrate_add_log_group_id():
    """
    Adds the log_group_id column to existing databases created before this
    feature existed. Base.metadata.create_all() only creates missing tables,
    not missing columns on existing tables, so this covers upgrades in place
    without touching any data already logged.
    """
    with engine.connect() as conn:
        existing_cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(sessions)")]
        if "log_group_id" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE sessions ADD COLUMN log_group_id VARCHAR")
            conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
