import pandas as pd
import io
import sqlite3
import numpy as np
import math
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body, Query
from app import models
from app.database import get_db, engine
from datetime import date
from sqlalchemy.sql import text as sql_text

router = APIRouter()

def log_anomaly_to_db(connection, turbine_id: int, timestamp: str, metric: str, alert_type: str, severity: str, actual: float, threshold: float, description: str):
    """Helper to insert a detailed anomaly record into the alerts table."""
    with connection.begin():
        connection.execute(
            sql_text("""
                INSERT INTO alerts (turbine_id, timestamp, metric, alert_type, severity, actual_value, threshold_value, description) 
                VALUES (:turbine_id, :timestamp, :metric, :alert_type, :severity, :actual_value, :threshold_value, :description)
            """),
            {
                "turbine_id": turbine_id, "timestamp": timestamp, "metric": metric, "alert_type": alert_type,
                "severity": severity, "actual_value": actual, "threshold_value": threshold, "description": description
            }
        )

@router.get("/sensor-metrics/{turbine_id}", response_model=models.PaginatedTurbineReadings, summary="Get Recent Sensor Metrics with Pagination")
def get_sensor_metrics(
    turbine_id: int, 
    page: int = Query(1, ge=1, description="Page number to retrieve"), 
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"), 
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves a paginated list of sensor readings for a specific turbine.
    """
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sensor_readings WHERE turbine_id = ?", (turbine_id,))
    total_items = cursor.fetchone()[0]
    total_pages = math.ceil(total_items / page_size)

    offset = (page - 1) * page_size
    cursor.execute(
        "SELECT * FROM sensor_readings WHERE turbine_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        (turbine_id, page_size, offset)
    )
    readings = cursor.fetchall()

    return {
        "data": [dict(row) for row in readings],
         "metadata": {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": len(readings)
        },
    }

@router.get("/health-summary", response_model=models.PaginatedHealthSummary, summary="Get Paginated Health Summary for Turbines")
def get_health_summary(
    page: int = Query(1, ge=1, description="Page number of turbines to analyze"), 
    page_size: int = Query(10, ge=1, le=50, description="Number of turbines per page"), 
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Calculates and returns a health summary. The pagination is applied to the list of turbines
    to ensure the calculation is performed on a manageable subset of data.
    """
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT turbine_id FROM sensor_readings ORDER BY turbine_id")
    turbine_ids = [row[0] for row in cursor.fetchall()]

    total_items = len(turbine_ids)
    total_pages = math.ceil(total_items / page_size)

    offset = (page - 1) * page_size
    paginated_ids = turbine_ids[offset : offset + page_size]

    if not paginated_ids:
        return { "data": [], "metadata": {"total_items": total_items, "total_pages": total_pages, "current_page": page, "page_size": 0},}
    
    placeholders = ','.join('?' for _ in paginated_ids)
    query = f"SELECT * FROM sensor_readings WHERE turbine_id IN ({placeholders})"
    
    df = pd.read_sql_query(query, db, params=paginated_ids)
    
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
        record_count=('mf', 'count'), total_fuel_usage=('mf', 'sum'),
        avg_shaft_torque_gtt=('gtt', 'mean'), avg_exit_temp_t48=('t48', 'mean'),
        avg_pressure_ratio=('pressure_ratio', 'mean'), avg_thermal_efficiency_percent=('thermal_efficiency', 'mean'),
        avg_compressor_efficiency_percent=('compressor_efficiency', 'mean'),
        avg_compressor_decay=('decay_coeff_comp', 'mean'), avg_turbine_decay=('decay_coeff_turbine', 'mean'),
        avg_power_proxy_kw=('power_proxy_kw', 'mean'), avg_total_decay_score=('total_decay_score', 'mean'),
        avg_temp_ratio_t48_p48=('temp_ratio_t48_p48', 'mean'), avg_temp_ratio_t1_p1=('temp_ratio_t1_p1', 'mean'),
        avg_temp_ratio_t2_p2=('temp_ratio_t2_p2', 'mean'), avg_torque_diff=('torque_diff', 'mean'),
        avg_rpm_ratio_gtn_ggn=('rpm_ratio_gtn_ggn', 'mean'), avg_fuel_per_rpm=('fuel_per_rpm', 'mean'),
        avg_total_prop_torque=('total_prop_torque', 'mean')
    ).reset_index()

    results = summary_groups.to_dict(orient='records')
    return {
       
        "data": results,
         "metadata": {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": len(results)
        },
    }


@router.post("/upload-data/{turbine_id}", status_code=status.HTTP_201_CREATED, summary="Upload, Process, Store, and Analyze Data for Anomalies (ETL)")
def upload_sensor_data_from_csv(turbine_id: int, file: UploadFile = File(...), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT turbine_id FROM turbine_metadata WHERE turbine_id = ?", (turbine_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Turbine with ID {turbine_id} not found.")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = file.file.read()
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
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.to_datetime(pd.Timestamp.now()).strftime('%Y-%m-%d %H:%M:%S')

    alerts_to_log = []
    t48_alerts = df[df['t48'] > 600].copy()
    if not t48_alerts.empty:
        t48_alerts['metric'], t48_alerts['alert_type'], t48_alerts['severity'] = 't48', 'Overheat', 'Critical'
        t48_alerts['actual_value'], t48_alerts['threshold_value'] = t48_alerts['t48'], 900.0
        t48_alerts['description'] = t48_alerts.apply(lambda row: f"T48={row['t48']:.2f}°C exceeds threshold", axis=1)
        alerts_to_log.append(t48_alerts)
    
    mf_alerts = df[df['mf'] > 0.3].copy()
    if not mf_alerts.empty:
        mf_alerts['metric'], mf_alerts['alert_type'], mf_alerts['severity'] = 'mf', 'High Fuel Flow', 'Critical'
        mf_alerts['actual_value'], mf_alerts['threshold_value'] = mf_alerts['mf'], 0.3
        mf_alerts['description'] = mf_alerts.apply(lambda row: f"mf={row['mf']:.2f} kg/s exceeds threshold", axis=1)
        alerts_to_log.append(mf_alerts)

    alerts_found = 0
    try:
        if alerts_to_log:
            alert_cols = ['turbine_id', 'timestamp', 'metric', 'alert_type', 'severity', 'actual_value', 'threshold_value', 'description']
            all_alerts_df = pd.concat(alerts_to_log, ignore_index=True)
            all_alerts_df['turbine_id'] = turbine_id
            final_alerts_df = all_alerts_df[alert_cols]
            alerts_found = len(final_alerts_df)
            final_alerts_df.to_sql('alerts', con=db, if_exists='append', index=False)

        df = df.round(4)
        df['turbine_id'] = turbine_id
        load_df = df[required_cols + ['turbine_id']]
        load_df.to_sql('sensor_readings', con=db, if_exists='append', index=False)

        db.commit()
        
        response_message = f"Successfully processed and loaded {len(load_df)} records for turbine ID {turbine_id}."
        if alerts_found > 0:
            response_message += f" Found and logged {alerts_found} anomalies."
        return {"message": response_message, "anomalies_logged_count": alerts_found}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to load data into database: {e}")


@router.post("/alerts", response_model=models.Alert, status_code=status.HTTP_201_CREATED, summary="Log a New Anomaly Alert")
def log_alert(alert: models.AlertCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
             """
            INSERT INTO alerts (turbine_id, timestamp, metric, alert_type, severity, actual_value, threshold_value, description) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (alert.turbine_id, alert.timestamp, alert.metric, alert.alert_type, alert.severity, 
             alert.actual_value, alert.threshold_value, alert.description)
        )
        db.commit()
        alert_id = cursor.lastrowid
        return models.Alert(alert_id=alert_id, **alert.model_dump())
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

@router.get("/alerts", response_model=models.PaginatedAlerts, summary="Get Paginated Anomaly Alerts with Date Filter")
def get_alerts(
    turbine_id: Optional[int] = None, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None, 
    page: int = Query(1, ge=1, description="Page number to retrieve"), 
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"), 
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves a paginated list of alerts, with optional filters for turbine ID and date range.
    """
    cursor = db.cursor()
    
    where_clause = "WHERE 1=1"
    params = []
    if turbine_id:
        where_clause += " AND turbine_id = ?"
        params.append(turbine_id)
    if start_date and end_date:
        where_clause += " AND date(timestamp) BETWEEN ? AND ?"
        params.extend([start_date.isoformat(), end_date.isoformat()])
        
    count_query = f"SELECT COUNT(*) FROM alerts {where_clause}"
    cursor.execute(count_query, params)
    total_items = cursor.fetchone()[0]
    total_pages = math.ceil(total_items / page_size)

    offset = (page - 1) * page_size
    data_query = f"SELECT * FROM alerts {where_clause} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    cursor.execute(data_query, params)
    alerts = cursor.fetchall()
    
    return {
      
        "data": [dict(row) for row in alerts],
        "metadata": {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": len(alerts)
        },
    }

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
    timestamp_str = reading_data.timestamp.isoformat()
    
    if reading_data.t48 > 950:
        desc = f"Critical Turbine Exit Temperature: {reading_data.t48:.2f} °C"
        cursor.execute(
            "INSERT INTO alerts (turbine_id, timestamp, metric, alert_type, severity, actual_value, threshold_value, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (turbine_id, timestamp_str, "t48", "Overheat", "High", reading_data.t48, 950.0, desc)
        )

    if reading_data.decay_coeff_turbine < 0.96:
        desc = f"Medium Turbine Decay Detected: {reading_data.decay_coeff_turbine:.4f}"
        cursor.execute(
            "INSERT INTO alerts (turbine_id, timestamp, metric, alert_type, severity, actual_value, threshold_value, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (turbine_id, timestamp_str, "decay_coeff_turbine", "Component Decay", "Medium", reading_data.decay_coeff_turbine, 0.96, desc)
        )

    if reading_data.decay_coeff_comp < 0.96:
        desc = f"Medium Compressor Decay Detected: {reading_data.decay_coeff_comp:.4f}"
        cursor.execute(
            "INSERT INTO alerts (turbine_id, timestamp, metric, alert_type, severity, actual_value, threshold_value, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (turbine_id, timestamp_str, "decay_coeff_comp", "Component Decay", "Medium", reading_data.decay_coeff_comp, 0.96, desc)
        )
        
    if pressure_ratio < 9.0 and reading_data.gtn > 1500: 
        desc = f"Low Pressure Ratio at Speed: {pressure_ratio:.2f}"
        cursor.execute(
            "INSERT INTO alerts (turbine_id, timestamp, metric, alert_type, severity, actual_value, threshold_value, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (turbine_id, timestamp_str, "pressure_ratio", "Pressure Anomaly", "Low", pressure_ratio, 9.0, desc)
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

