import pytest
import sqlite3
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app import database
from app.database import get_db

@pytest.fixture(scope="function")
def client(tmp_path, monkeypatch):
    """
    This is the master fixture that sets up a fully isolated test environment.
    """
    TEST_DB_PATH = tmp_path / "test_turbine_data.db"
    TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

    conn = sqlite3.connect(TEST_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE turbine_metadata (turbine_id INTEGER PRIMARY KEY, location TEXT, model TEXT, manufacturer TEXT);")
    cursor.execute("CREATE TABLE sensor_readings (id INTEGER PRIMARY KEY, turbine_id INTEGER, timestamp TEXT, t48 REAL, mf REAL, ts REAL, tp REAL, gtn REAL, p1 REAL, p2 REAL, decay_coeff_comp REAL, decay_coeff_turbine REAL, lp REAL, v REAL, gtt REAL, ggn REAL, t1 REAL, t2 REAL, p48 REAL, pexh REAL, tic REAL);")
    cursor.execute("CREATE TABLE alerts (alert_id INTEGER PRIMARY KEY, turbine_id INTEGER, timestamp TEXT, metric TEXT, alert_type TEXT, severity TEXT, actual_value REAL, threshold_value REAL, description TEXT);")
    cursor.execute("INSERT INTO turbine_metadata (turbine_id, location, manufacturer, model) VALUES (1, 'North Sea', 'Siemens', 'V90');")
    cursor.execute("INSERT INTO turbine_metadata (turbine_id, location, manufacturer, model) VALUES (2, 'Baltic Sea', 'Vestas', 'V112');")
    conn.commit()
    conn.close()

    test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

    monkeypatch.setattr(database, "DATABASE_PATH", TEST_DB_PATH)
    monkeypatch.setattr(database, "engine", test_engine)

    def override_get_db():
        db_conn = sqlite3.connect(TEST_DB_PATH, check_same_thread=False)
        db_conn.row_factory = sqlite3.Row
        try:
            yield db_conn
        finally:
            db_conn.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()