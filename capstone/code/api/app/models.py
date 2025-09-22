from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, timedelta, datetime

# Turbine Management Models
class TurbineBase(BaseModel):
    location: Optional[str] = Field(None, example="North Sea Platform Alpha")
    manufacturer: Optional[str] = Field(None, example="Siemens")
    model: Optional[str] = Field(None, example="SGT-400")

class TurbineCreate(TurbineBase):
    pass

class TurbineUpdate(TurbineBase):
    pass

class Turbine(TurbineBase):
    turbine_id: int
    class Config:
        from_attributes = True

# RESTORED MODEL: Contains only the fields stored in the database
class TurbineReading(BaseModel):
    lp: float
    v: float
    gtt: float
    gtn: float
    ggn: float
    ts: float
    tp: float
    t48: float
    t1: float
    t2: float
    p48: float
    p1: float
    p2: float
    pexh: float
    tic: float
    mf: float
    decay_coeff_comp: float
    decay_coeff_turbine: float
    turbine_id: int
    class Config:
        from_attributes = True

class HealthSummary(BaseModel):
    turbine_id: int
    record_count: int
    total_fuel_usage: float
    avg_shaft_torque_gtt: float
    avg_exit_temp_t48: float
    avg_pressure_ratio: float
    avg_thermal_efficiency_percent: float
    avg_compressor_efficiency_percent: float
    avg_compressor_decay: float
    avg_turbine_decay: float

class Stats(BaseModel):
    min: float
    avg: float
    max: float

class CompressorStats(BaseModel):
    inlet_temp_t1: Stats
    outlet_temp_t2: Stats
    inlet_pressure_p1: Stats
    outlet_pressure_p2: Stats
    pressure_ratio: Stats

class TurbineStats(BaseModel):
    exit_temp_t48: Stats
    exit_pressure_p48: Stats
    shaft_torque_gtt: Stats
    rpm_gtn: Stats
    generator_rpm_ggn: Stats

class EfficiencyMetrics(BaseModel):
    thermal_efficiency_percent: Stats
    compressor_efficiency_percent: Stats

class TurbineAnalyticsReport(BaseModel):
    record_count: int
    period_start: str
    period_end: str
    compressor_stats: CompressorStats
    turbine_stats: TurbineStats
    efficiency_metrics: EfficiencyMetrics

class TimeFilterRequest(BaseModel):
    turbine_ids: List[int] = Field(default=[1])
    start_date: Optional[date] = Field(default=None, description="Optional start date for the report period.")
    end_date: Optional[date] = Field(default=None, description="Optional end date for the report period.")

class AnomalyAlertBase(BaseModel):
    turbine_id: int = Field(default=1)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), example="2025-09-22T12:30:00Z")
    description: str = Field(..., example="High pressure spike in compressor outlet.")
    severity: str = Field(..., example="High")

class AnomalyAlertCreate(AnomalyAlertBase):
    pass

class AnomalyAlert(AnomalyAlertBase):
    id: int
    class Config:
        from_attributes = True

class TurbineReadingBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    lp: float
    v: float
    gtt: float
    gtn: float
    ggn: float
    ts: float
    tp: float
    t48: float
    t1: float
    t2: float
    p48: float
    p1: float
    p2: float
    pexh: float
    tic: float
    mf: float
    decay_coeff_comp: float
    decay_coeff_turbine: float

class TurbineReadingCreate(TurbineReadingBase):
    pass