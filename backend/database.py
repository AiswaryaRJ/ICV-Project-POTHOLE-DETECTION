import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "roadsense.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # Low, Medium, High
    status = Column(String, default="Reported") # Reported, Dispatched, In progress, Repaired
    snapshot_path = Column(String, nullable=True)
    repair_proof_path = Column(String, nullable=True)
    street_name = Column(String, default="Main Arterial Sector 4")
    priority = Column(String, default="Medium") # Low, Medium, High, Urgent
    is_simulated_gps = Column(Boolean, default=True)

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, index=True)
    title = Column(String, nullable=False)
    assignee = Column(String, default="Unassigned")
    priority = Column(String, default="Medium")
    status = Column(String, default="Reported")
    notes = Column(Text, default="")
    repair_proof_path = Column(String, nullable=True)
    cost_estimate = Column(Float, default=250.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SettingsModel(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    model_path = Column(String, default="models/best.pt")
    input_size = Column(Integer, default=640)
    default_conf = Column(Float, default=0.25)
    gps_mode = Column(String, default="Simulated")
    custom_gps_path = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(SettingsModel).first():
        db.add(SettingsModel())
        db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
