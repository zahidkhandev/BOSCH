# app/database.py

import sqlite3
from sqlalchemy import create_engine
from pathlib import Path

# --- Database Setup (Modified) ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "data" / "turbine_data.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    """Initializes all tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    # Create turbine_metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS turbine_metadata (
        turbine_id INTEGER PRIMARY KEY, location TEXT, manufacturer TEXT, model TEXT, install_date DATE
    );
    """)
    # Create sensor_readings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, lp FLOAT, v FLOAT, gtt FLOAT, gtn FLOAT, ggn FLOAT,
        ts FLOAT, tp FLOAT, t48 FLOAT, t1 FLOAT, t2 FLOAT, p48 FLOAT, p1 FLOAT, p2 FLOAT, pexh FLOAT, tic FLOAT,
        mf FLOAT, decay_coeff_comp FLOAT, decay_coeff_turbine FLOAT, turbine_id INTEGER,
        FOREIGN KEY (turbine_id) REFERENCES turbine_metadata(turbine_id)
    );
    """)
    # Create alerts table (Modified)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        turbine_id INTEGER,
        timestamp TEXT,
        metric TEXT,
        alert_type TEXT,
        severity TEXT,
        actual_value FLOAT,
        threshold_value FLOAT,
        description TEXT,
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