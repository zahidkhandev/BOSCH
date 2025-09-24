
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class PaginationMetadata(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    page_size: int

class AlertBase(BaseModel):
    turbine_id: int = Field(default=1)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), json_schema_extra={"example": "2025-09-22T12:30:00Z"})
    metric: str = Field(..., json_schema_extra={"example": "t48"})
    alert_type: str = Field(..., json_schema_extra={"example": "Overheat"})
    severity: str = Field(..., json_schema_extra={"example": "High"})
    actual_value: float = Field(..., json_schema_extra={"example": 960.5})
    threshold_value: float = Field(..., json_schema_extra={"example": 950.0})
    description: str = Field(..., json_schema_extra={"example": "High pressure spike in compressor outlet."})

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    alert_id: int
    model_config = {
        "from_attributes": True
    }

class PaginatedAlerts(BaseModel):
    data: List[Alert]
    metadata: PaginationMetadata

class TurbineBase(BaseModel):
    location: Optional[str] = Field(None, json_schema_extra={"example": "North Sea Platform Alpha"})
    manufacturer: Optional[str] = Field(None, json_schema_extra={"example": "Siemens"})
    model: Optional[str] = Field(None, json_schema_extra={"example": "SGT-400"})

class TurbineCreate(TurbineBase):
    pass

class TurbineUpdate(TurbineBase):
    pass

class Turbine(TurbineBase):
    turbine_id: int
    model_config = {
        "from_attributes": True
    }
        
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
    model_config = {
        "from_attributes": True
    }

class PaginatedTurbineReadings(BaseModel):
    data: List[TurbineReading]
    metadata: PaginationMetadata

class TurbineReadingCreate(BaseModel):
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
    avg_power_proxy_kw: float
    avg_total_decay_score: float
    avg_temp_ratio_t48_p48: float
    avg_temp_ratio_t1_p1: float
    avg_temp_ratio_t2_p2: float
    avg_torque_diff: float
    avg_rpm_ratio_gtn_ggn: float
    avg_fuel_per_rpm: float
    avg_total_prop_torque: float

class PaginatedHealthSummary(BaseModel):
    data: List[HealthSummary]
    metadata: PaginationMetadata

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
    power_proxy_kw: Stats

class EfficiencyMetrics(BaseModel):
    thermal_efficiency_percent: Stats
    compressor_efficiency_percent: Stats
    fuel_per_rpm: Stats
    rpm_ratio_gtn_ggn: Stats
    
class DecayMetrics(BaseModel):
    total_decay_score: Stats
    
class TemperaturePressureRatios(BaseModel):
    temp_ratio_t48_p48: Stats
    temp_ratio_t1_p1: Stats
    temp_ratio_t2_p2: Stats

class TorqueMetrics(BaseModel):
    torque_diff: Stats
    total_prop_torque: Stats

class TurbineAnalyticsReport(BaseModel):
    record_count: int
    period_start: str
    period_end: str
    compressor_stats: CompressorStats
    turbine_stats: TurbineStats
    efficiency_metrics: EfficiencyMetrics
    decay_metrics: DecayMetrics
    temp_pressure_ratios: TemperaturePressureRatios
    torque_metrics: TorqueMetrics

class TimeFilterRequest(BaseModel):
    turbine_ids: List[int] = Field(default=[1])
    start_date: Optional[date] = Field(default=None, description="Optional start date for the report period.")
    end_date: Optional[date] = Field(default=None, description="Optional end date for the report period.")