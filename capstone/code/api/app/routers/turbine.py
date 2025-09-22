import pandas as pd
import io
import sqlite3
import numpy as np
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from app import models
from app.database import get_db, engine
from datetime import date
from sqlalchemy.sql import text as sql_text

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

@router.get("/health-summary", response_model=List[models.HealthSummary], summary="Get Enriched Health Summary for All Turbines (Phase 5)")
def get_health_summary(db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM sensor_readings"
    df = pd.read_sql_query(query, db)
    if df.empty:
        raise HTTPException(status_code=404, detail="No health summary data found.")

    gamma = 1.4
    k_to_c = 273.15
    
    df['pressure_ratio'] = df['p2'] / df['p1']
    t1_k, t2_k = df['t1'] + k_to_c, df['t2'] + k_to_c
    t2s_k = t1_k * (df['pressure_ratio']**((gamma - 1) / gamma))
    df['compressor_efficiency'] = ((t2s_k - t1_k) / (t2_k - t1_k)) * 100
    df['thermal_efficiency'] = (1 - (1 / (df['pressure_ratio']**((gamma - 1) / gamma)))) * 100
    
    df['temp_ratio_t48_p48'] = df['t48'] / df['p48']
    df['temp_ratio_t1_p1'] = df['t1'] / df['p1']
    df['temp_ratio_t2_p2'] = df['t2'] / df['p2']
    df['torque_diff'] = df['ts'] - df['tp']
    df['rpm_ratio_gtn_ggn'] = df['gtn'] / df['ggn']
    df['fuel_per_rpm'] = df['mf'] / df['gtn']
    df['total_prop_torque'] = df['ts'] + df['tp']
    
    angular_velocity_rad_s = df['gtn'] * (2 * np.pi / 60)
    df['power_proxy_kw'] = (df['gtt'] * angular_velocity_rad_s)
    df['total_decay_score'] = (1 - df['decay_coeff_comp']) + (1 - df['decay_coeff_turbine'])
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    summary_groups = df.groupby('turbine_id').agg(
        record_count=('mf', 'count'),
        total_fuel_usage=('mf', 'sum'),
        avg_shaft_torque_gtt=('gtt', 'mean'),
        avg_exit_temp_t48=('t48', 'mean'),
        avg_pressure_ratio=('pressure_ratio', 'mean'),
        avg_thermal_efficiency_percent=('thermal_efficiency', 'mean'),
        avg_compressor_efficiency_percent=('compressor_efficiency', 'mean'),
        avg_compressor_decay=('decay_coeff_comp', 'mean'),
        avg_turbine_decay=('decay_coeff_turbine', 'mean'),
        avg_power_proxy_kw=('power_proxy_kw', 'mean'),
        avg_total_decay_score=('total_decay_score', 'mean'),
        avg_temp_ratio_t48_p48=('temp_ratio_t48_p48', 'mean'),
        avg_temp_ratio_t1_p1=('temp_ratio_t1_p1', 'mean'),
        avg_temp_ratio_t2_p2=('temp_ratio_t2_p2', 'mean'),
        avg_torque_diff=('torque_diff', 'mean'),
        avg_rpm_ratio_gtn_ggn=('rpm_ratio_gtn_ggn', 'mean'),
        avg_fuel_per_rpm=('fuel_per_rpm', 'mean'),
        avg_total_prop_torque=('total_prop_torque', 'mean')
    ).reset_index()

    return summary_groups.to_dict(orient='records')

def log_anomaly(turbine_id: int, timestamp: str, description: str, severity: str):
    with engine.connect() as connection:
        with connection.begin(): 
            connection.execute(
                sql_text("""
                    INSERT INTO anomaly_alerts (turbine_id, timestamp, description, severity) 
                    VALUES (:turbine_id, :timestamp, :description, :severity)
                """),
                {
                    "turbine_id": turbine_id, "timestamp": timestamp, 
                    "description": description, "severity": severity
                }
            )

@router.post("/upload-data/{turbine_id}", status_code=status.HTTP_201_CREATED, summary="Upload, Process, Store, and Analyze Data for Anomalies (ETL)")
async def upload_sensor_data_from_csv(turbine_id: int, file: UploadFile = File(...)):
    with engine.connect() as connection:
        result = connection.execute(
            sql_text("SELECT turbine_id FROM turbine_metadata WHERE turbine_id = :id"),
            {"id": turbine_id}
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail=f"Turbine with ID {turbine_id} not found.")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        df.rename(columns=lambda x: x.lower().strip(), inplace=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read or parse CSV file: {e}")

    column_mapping = {
        "lever position (lp)": "lp", "ship speed (v) [knots]": "v", "gas turbine shaft torque (gtt) [kn/m]": "gtt",
        "gas turbine revolutions (gtn) [rpm]": "gtn", "gas generator revolutions (ggn) [rpm]": "ggn",
        "starboard propeller torque (ts) [kn/m]": "ts", "port propeller torque (tp) [kn/m]": "tp",
        "hp turbine exit temperature (t48) [°c]": "t48", "compressor inlet air temperature (t1) [°c]": "t1",
        "compressor outlet air temperature (t2) [°c]": "t2", "hp turbine exit pressure (p48) [bar]": "p48",
        "compressor inlet air pressure (p1) [bar]": "p1", "compressor outlet air pressure (p2) [bar]": "p2",
        "exhaust gas pressure [bar]": "pexh", "turbine injection control (tic) [%]": "tic",
        "fuel flow (mf) [kg/s]": "mf", "compressor decay coefficient": "decay_coeff_comp",
        "turbine decay coefficient": "decay_coeff_turbine"
    }
    df.rename(columns=column_mapping, inplace=True)
    
    required_cols = list(column_mapping.values())
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {missing_cols}")

    df.drop_duplicates(inplace=True)
    for col in required_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if 'index' in numeric_cols: numeric_cols.remove('index')
    
    for col in numeric_cols:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        df[col] = df[col].clip(lower_bound, upper_bound)
        
    df[numeric_cols] = df[numeric_cols].rolling(window=3, min_periods=1).mean()
    df['pressure_ratio'] = df['p2'] / df['p1']
    
    alerts_found = []
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.to_datetime(pd.Timestamp.now()).strftime('%Y-%m-%d %H:%M:%S')

    for index, row in df.iterrows():
        if row['t48'] > 950:
            desc = f"Critical Turbine Exit Temperature: {row['t48']:.2f} °C"
            log_anomaly(turbine_id, row['timestamp'], desc, "High")
            alerts_found.append(desc)
        if row['decay_coeff_turbine'] < 0.96:
            desc = f"Medium Turbine Decay Detected: {row['decay_coeff_turbine']:.4f}"
            log_anomaly(turbine_id, row['timestamp'], desc, "Medium")
            alerts_found.append(desc)
        if row['decay_coeff_comp'] < 0.96:
            desc = f"Medium Compressor Decay Detected: {row['decay_coeff_comp']:.4f}"
            log_anomaly(turbine_id, row['timestamp'], desc, "Medium")
            alerts_found.append(desc)
        if row['pressure_ratio'] < 9.0 and row['gtn'] > 1500:
            desc = f"Low Pressure Ratio at Speed: {row['pressure_ratio']:.2f}"
            log_anomaly(turbine_id, row['timestamp'], desc, "Low")
            alerts_found.append(desc)

    df = df.round(4)
    df['turbine_id'] = turbine_id
    load_df = df[required_cols + ['turbine_id']]
    
    try:
        load_df.to_sql('sensor_readings', con=engine, if_exists='append', index=False)
        response_message = f"Successfully processed and loaded {len(load_df)} records for turbine ID {turbine_id}."
        if alerts_found:
            response_message += f" Found and logged {len(alerts_found)} anomalies."
        return {"message": response_message, "anomalies_logged": alerts_found}
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
    
    if filters.start_date and filters.end_date:
        query = f"SELECT * FROM sensor_readings WHERE date(timestamp) BETWEEN ? AND ? AND turbine_id IN ({placeholders})"
        params = [filters.start_date.isoformat(), filters.end_date.isoformat()] + filters.turbine_ids
    else:
        query = f"SELECT * FROM sensor_readings WHERE turbine_id IN ({placeholders})"
        params = filters.turbine_ids

    df = pd.read_sql_query(query, db, params=params)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for the specified filters.")
    
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
    
    df['temp_ratio_t48_p48'] = df['t48'] / df['p48']
    df['temp_ratio_t1_p1'] = df['t1'] / df['p1']
    df['temp_ratio_t2_p2'] = df['t2'] / df['p2']
    df['torque_diff'] = df['ts'] - df['tp']
    df['rpm_ratio_gtn_ggn'] = df['gtn'] / df['ggn']
    df['fuel_per_rpm'] = df['mf'] / df['gtn']
    df['total_prop_torque'] = df['ts'] + df['tp']
    angular_velocity_rad_s = df['gtn'] * (2 * np.pi / 60)
    df['power_proxy_kw'] = df['gtt'] * angular_velocity_rad_s
    df['total_decay_score'] = (1 - df['decay_coeff_comp']) + (1 - df['decay_coeff_turbine'])

    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    def get_stats(series):
        series.fillna(0, inplace=True)
        return models.Stats(min=series.min(), avg=series.mean(), max=series.max())

    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()

    return models.TurbineAnalyticsReport(
        record_count=len(df),
        period_start=str(start_time) if pd.notna(start_time) else "N/A",
        period_end=str(end_time) if pd.notna(end_time) else "N/A",
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
            generator_rpm_ggn=get_stats(df['ggn']),
            power_proxy_kw=get_stats(df['power_proxy_kw'])
        ),
        efficiency_metrics=models.EfficiencyMetrics(
            thermal_efficiency_percent=get_stats(df['thermal_efficiency']),
            compressor_efficiency_percent=get_stats(df['compressor_efficiency']),
            fuel_per_rpm=get_stats(df['fuel_per_rpm']),
            rpm_ratio_gtn_ggn=get_stats(df['rpm_ratio_gtn_ggn'])
        ),
        decay_metrics=models.DecayMetrics(
            total_decay_score=get_stats(df['total_decay_score'])
        ),
        temp_pressure_ratios=models.TemperaturePressureRatios(
            temp_ratio_t48_p48=get_stats(df['temp_ratio_t48_p48']),
            temp_ratio_t1_p1=get_stats(df['temp_ratio_t1_p1']),
            temp_ratio_t2_p2=get_stats(df['temp_ratio_t2_p2'])
        ),
        torque_metrics=models.TorqueMetrics(
            torque_diff=get_stats(df['torque_diff']),
            total_prop_torque=get_stats(df['total_prop_torque'])
        )
    )

@router.post("/sensor-reading/{turbine_id}", response_model=models.TurbineReading, status_code=status.HTTP_201_CREATED, summary="Append a Single Sensor Reading and Check for Anomalies")
def log_single_reading(turbine_id: int, reading_data: models.TurbineReadingCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT turbine_id FROM turbine_metadata WHERE turbine_id = ?", (turbine_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Turbine with ID {turbine_id} not found.")

    
    pressure_ratio = reading_data.p2 / reading_data.p1 if reading_data.p1 != 0 else 0
    
    if reading_data.t48 > 950:
        desc = f"Critical Turbine Exit Temperature: {reading_data.t48:.2f} °C"
        cursor.execute(
            "INSERT INTO anomaly_alerts (turbine_id, timestamp, description, severity) VALUES (?, ?, ?, ?)",
            (turbine_id, reading_data.timestamp.isoformat(), desc, "High")
        )

    if reading_data.decay_coeff_turbine < 0.96:
        desc = f"Medium Turbine Decay Detected: {reading_data.decay_coeff_turbine:.4f}"
        cursor.execute(
            "INSERT INTO anomaly_alerts (turbine_id, timestamp, description, severity) VALUES (?, ?, ?, ?)",
            (turbine_id, reading_data.timestamp.isoformat(), desc, "Medium")
        )

    if reading_data.decay_coeff_comp < 0.96:
        desc = f"Medium Compressor Decay Detected: {reading_data.decay_coeff_comp:.4f}"
        cursor.execute(
            "INSERT INTO anomaly_alerts (turbine_id, timestamp, description, severity) VALUES (?, ?, ?, ?)",
            (turbine_id, reading_data.timestamp.isoformat(), desc, "Medium")
        )
        
    if pressure_ratio < 9.0 and reading_data.gtn > 1500: 
        desc = f"Low Pressure Ratio at Speed: {pressure_ratio:.2f}"
        cursor.execute(
            "INSERT INTO anomaly_alerts (turbine_id, timestamp, description, severity) VALUES (?, ?, ?, ?)",
            (turbine_id, reading_data.timestamp.isoformat(), desc, "Low")
        )

    columns = [
        'timestamp', 'lp', 'v', 'gtt', 'gtn', 'ggn', 'ts', 'tp', 't48', 't1', 't2',
        'p48', 'p1', 'p2', 'pexh', 'tic', 'mf', 'decay_coeff_comp', 'decay_coeff_turbine',
        'turbine_id'
    ]
    placeholders = ', '.join('?' for _ in columns)
    
    data_to_insert = (
        reading_data.timestamp.isoformat(), reading_data.lp, reading_data.v, reading_data.gtt, reading_data.gtn,
        reading_data.ggn, reading_data.ts, reading_data.tp, reading_data.t48, reading_data.t1,
        reading_data.t2, reading_data.p48, reading_data.p1, reading_data.p2, reading_data.pexh,
        reading_data.tic, reading_data.mf, reading_data.decay_coeff_comp,
        reading_data.decay_coeff_turbine, turbine_id
    )
    
    try:
        query = f"INSERT INTO sensor_readings ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(query, data_to_insert)
        
        db.commit()
        
        new_record_id = cursor.lastrowid
        cursor.execute("SELECT * FROM sensor_readings WHERE id = ?", (new_record_id,))
        new_record = cursor.fetchone()
        return dict(new_record)
        
    except sqlite3.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {e}")