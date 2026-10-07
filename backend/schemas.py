from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DetectionOut(BaseModel):
    id: int
    code: str
    timestamp: datetime
    lat: float
    lon: float
    confidence: float
    severity: str
    status: str
    snapshot_path: Optional[str]
    repair_proof_path: Optional[str] = None
    street_name: Optional[str] = "Main Arterial Sector 4"
    priority: Optional[str] = "Medium"
    is_simulated_gps: bool

    class Config:
        from_attributes = True

class WorkOrderOut(BaseModel):
    id: int
    detection_id: int
    title: str
    assignee: str
    priority: str
    status: str
    notes: str
    repair_proof_path: Optional[str] = None
    cost_estimate: Optional[float] = 250.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    repair_proof_path: Optional[str] = None

class WorkOrderCreate(BaseModel):
    detection_id: int
    title: Optional[str] = None
    assignee: Optional[str] = "Unassigned"
    priority: Optional[str] = "Medium"
    notes: Optional[str] = ""

class BulkStatusUpdate(BaseModel):
    ids: List[int]
    status: str

class SettingsOut(BaseModel):
    model_path: str
    model_loaded: bool
    input_size: int
    default_conf: float
    gps_mode: str
    custom_gps_path: Optional[str]

class SettingsUpdate(BaseModel):
    model_path: Optional[str] = None
    input_size: Optional[int] = None
    default_conf: Optional[float] = None
    gps_mode: Optional[str] = None
