from pydantic import BaseModel
from typing import List, Dict, Any

class KpiVolume(BaseModel):
    total_processed: int
    auto_accepted: int
    human_review: int
    llm_fallback: int

class ClassificationHealth(BaseModel):
    auto_accept_rate: float
    accuracy_estimate: float

class RiskSummary(BaseModel):
    critical: int
    high: int
    medium: int
    low: int

class ProcessingPerformance(BaseModel):
    avg_processing_time_sec: float
    total_volume_today: int

class DashboardKpisResponse(BaseModel):
    volume: KpiVolume
    classification_health: ClassificationHealth
    risk_summary: RiskSummary
    processing_performance: ProcessingPerformance

class TrendSeriesPoint(BaseModel):
    label: str
    value: float

class DashboardTrendsResponse(BaseModel):
    series: List[TrendSeriesPoint]
