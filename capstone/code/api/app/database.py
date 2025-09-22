import sqlite3
from sqlalchemy import create_engine
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "data" / "turbine_data.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turbine_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL,
        FOREIGN KEY (turbine_id) REFERENCES turbine_metadata(turbine_id)
    );
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
