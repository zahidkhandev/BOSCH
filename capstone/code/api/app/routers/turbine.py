import pandas as pd
import io
import sqlite3
import numpy as np
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from app import models
from app.database import get_db, engine
from datetime import date

router = APIRouter(
    prefix="/data",
    tags=["Turbine Data & Analytics"]
)

@router.get("/sensor-metrics/{turbine_id}", response_model=List[models.TurbineReading], summary="Get Recent Sensor Metrics (Phase 5)")
def get_sensor_metrics(turbine_id: int, limit: int = 10, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sensor_readings WHERE turbine_id = ? ORDER BY timestamp DESC LIMIT ?", (turbine_id, limit))
    readings = cursor.fetchall()
    if not readings:
        raise HTTPException(status_code=404, detail=f"No sensor metrics found for turbine ID {turbine_id}.")
    return [dict(row) for row in readings]

# REWRITTEN ENDPOINT
@router.get("/health-summary", response_model=List[models.HealthSummary], summary="Get Enriched Health Summary for All Turbines (Phase 5)")
def get_health_summary(db: sqlite3.Connection = Depends(get_db)):
    # This query fetches all data needed for the summary calculations.
    query = """
        SELECT turbine_id, mf, gtt, t48, p1, p2, t1, t2, decay_coeff_comp, decay_coeff_turbine 
        FROM sensor_readings
    """
    df = pd.read_sql_query(query, db)
    if df.empty:
        raise HTTPException(status_code=404, detail="No health summary data found.")

    # Calculate derived features
    gamma = 1.4
    k_to_c = 273.15
    df['pressure_ratio'] = df['p2'] / df['p1']
    t1_k, t2_k = df['t1'] + k_to_c, df['t2'] + k_to_c
    t2s_k = t1_k * (df['pressure_ratio']**((gamma - 1) / gamma))
    df['compressor_efficiency'] = ((t2s_k - t1_k) / (t2_k - t1_k)) * 100
    df['thermal_efficiency'] = (1 - (1 / (df['pressure_ratio']**((gamma - 1) / gamma)))) * 100
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Group by turbine and aggregate
    summary_groups = df.groupby('turbine_id').agg(
        record_count=('mf', 'count'),
        total_fuel_usage=('mf', 'sum'),
        avg_shaft_torque_gtt=('gtt', 'mean'),
        avg_exit_temp_t48=('t48', 'mean'),
        avg_pressure_ratio=('pressure_ratio', 'mean'),
        avg_thermal_efficiency_percent=('thermal_efficiency', 'mean'),
        avg_compressor_efficiency_percent=('compressor_efficiency', 'mean'),
        avg_compressor_decay=('decay_coeff_comp', 'mean'),
        avg_turbine_decay=('decay_coeff_turbine', 'mean')
    ).reset_index()

    # Convert to list of Pydantic models
    return summary_groups.to_dict(orient='records')

@router.post("/upload-data/{turbine_id}", status_code=status.HTTP_201_CREATED, summary="Upload, Process, and Store Sensor Data (ETL)")
async def upload_sensor_data_from_csv(turbine_id: int, file: UploadFile = File(...)):
    """
    This endpoint performs a full ETL (Extract, Transform, Load) pipeline on an uploaded CSV of sensor data.
    
    - **Extract**: Reads and validates the CSV data.
    - **Transform**: Cleans data, removes outliers, applies smoothing, and calculates derived features.
    - **Load**: Appends the fully processed data to the database for the specified turbine.
    """
    # --- Database Check (using the thread-safe engine) ---
    with engine.connect() as connection:
        result = connection.execute(
            sqlite3.text("SELECT turbine_id FROM turbine_metadata WHERE turbine_id = :id"),
            {"id": turbine_id}
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail=f"Turbine with ID {turbine_id} not found.")

    # --- 1. EXTRACT ---
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        df.columns = df.columns.str.lower()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read or parse CSV file: {e}")

    required_cols = ['lp', 'v', 'gtt', 'gtn', 'ggn', 'ts', 'tp', 't48', 't1', 't2', 'p48', 'p1', 'p2', 'pexh', 'tic', 'mf', 'decay_coeff_comp', 'decay_coeff_turbine']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {missing_cols}")

    # --- 2. TRANSFORM ---
    df.drop_duplicates(inplace=True)
    for col in required_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)

    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[col] = df[col].clip(lower_bound, upper_bound)
        
    df[numeric_cols] = df[numeric_cols].rolling(window=3, min_periods=1).mean()

    gamma = 1.4
    k_to_c = 273.15
    df['pressure_ratio'] = df['p2'] / df['p1']
    t1_k, t2_k = df['t1'] + k_to_c, df['t2'] + k_to_c
    t2s_k = t1_k * (df['pressure_ratio']**((gamma - 1) / gamma))
    df['compressor_efficiency'] = ((t2s_k - t1_k) / (t2_k - t1_k)) * 100
    df['thermal_efficiency'] = (1 - (1 / (df['pressure_ratio']**((gamma - 1) / gamma)))) * 100
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    angular_velocity_rad_s = df['gtn'] * (2 * np.pi / 60)
    df['power_proxy_kw'] = df['gtt'] * angular_velocity_rad_s
    df['total_decay_score'] = (1 - df['decay_coeff_comp']) + (1 - df['decay_coeff_turbine'])
    df['torque_diff'] = df['ts'] - df['tp']
    df['rpm_ratio_gtn_ggn'] = df['gtn'] / df['ggn']
    df['fuel_per_rpm'] = df['mf'] / df['gtn']
    df['total_prop_torque'] = df['ts'] + df['tp']

    df = df.round(4)
    df['turbine_id'] = turbine_id

    # --- 3. LOAD ---
    load_df = df[required_cols + ['turbine_id']]
    
    try:
        # Use the thread-safe engine for the database write operation
        load_df.to_sql('sensor_readings', con=engine, if_exists='append', index=False)
        return {"message": f"Successfully processed and loaded {len(load_df)} records for turbine ID {turbine_id}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data into database: {e}")

@router.post("/anomaly-alerts", response_model=models.AnomalyAlert, status_code=status.HTTP_201_CREATED, summary="Log a New Anomaly Alert (Phase 5)")
def log_anomaly_alert(alert: models.AnomalyAlertCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO anomaly_alerts (turbine_id, timestamp, description, severity) VALUES (?, ?, ?, ?)",
            (alert.turbine_id, alert.timestamp, alert.description, alert.severity)
        )
        db.commit()
        alert_id = cursor.lastrowid
        return models.AnomalyAlert(id=alert_id, **alert.model_dump())
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

@router.get("/anomaly-alerts", response_model=List[models.AnomalyAlert], summary="Get Anomaly Alerts with Date Filter")
def get_anomaly_alerts(turbine_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM anomaly_alerts WHERE 1=1"
    params = []
    if turbine_id:
        query += " AND turbine_id = ?"
        params.append(turbine_id)
    if start_date and end_date:
        query += " AND date(timestamp) BETWEEN ? AND ?"
        params.extend([start_date.isoformat(), end_date.isoformat()])
    
    cursor.execute(query, params)
    alerts = cursor.fetchall()
    return [dict(row) for row in alerts]

@router.post("/analytics-report", response_model=Dict[int, models.TurbineAnalyticsReport], summary="Get Advanced Analytics Report")
def get_analytics_report(filters: models.TimeFilterRequest = Body(...), db: sqlite3.Connection = Depends(get_db)):
    placeholders = ','.join('?' for _ in filters.turbine_ids)
    query = f"SELECT * FROM sensor_readings WHERE date(timestamp) BETWEEN ? AND ? AND turbine_id IN ({placeholders})"
    params = [filters.start_date.isoformat(), filters.end_date.isoformat()] + filters.turbine_ids

    df = pd.read_sql_query(query, db, params=params)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data for specified filters.")
    
    reports = {turbine_id: calculate_analytics(group) for turbine_id, group in df.groupby('turbine_id')}
    return reports

def calculate_analytics(df: pd.DataFrame):
    df.columns = df.columns.str.lower()
    gamma = 1.4
    k_to_c = 273.15
    df['pressure_ratio'] = df['p2'] / df['p1']
    t1_k, t2_k = df['t1'] + k_to_c, df['t2'] + k_to_c
    t2s_k = t1_k * (df['pressure_ratio']**((gamma - 1) / gamma))
    df['compressor_efficiency'] = ((t2s_k - t1_k) / (t2_k - t1_k)) * 100
    df['thermal_efficiency'] = (1 - (1 / (df['pressure_ratio']**((gamma - 1) / gamma)))) * 100
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    def get_stats(series):
        return models.Stats(min=series.min(), avg=series.mean(), max=series.max())

    return models.TurbineAnalyticsReport(
        record_count=len(df),
        period_start=df['timestamp'].min(),
        period_end=df['timestamp'].max(),
        compressor_stats=models.CompressorStats(
            inlet_temp_t1=get_stats(df['t1']),
            outlet_temp_t2=get_stats(df['t2']),
            inlet_pressure_p1=get_stats(df['p1']),
            outlet_pressure_p2=get_stats(df['p2']),
            pressure_ratio=get_stats(df['pressure_ratio'])
        ),
        turbine_stats=models.TurbineStats(
            exit_temp_t48=get_stats(df['t48']),
            exit_pressure_p48=get_stats(df['p48']),
            shaft_torque_gtt=get_stats(df['gtt']),
            rpm_gtn=get_stats(df['gtn']),
            generator_rpm_ggn=get_stats(df['ggn'])
        ),
        efficiency_metrics=models.EfficiencyMetrics(
            thermal_efficiency_percent=get_stats(df['thermal_efficiency']),
            compressor_efficiency_percent=get_stats(df['compressor_efficiency'])
        )
    )