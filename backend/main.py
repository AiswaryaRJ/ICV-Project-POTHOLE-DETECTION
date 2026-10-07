import os
import cv2
import csv
import io
import time
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import init_db, get_db, Detection, WorkOrder, SettingsModel
from backend.schemas import (
    DetectionOut, WorkOrderOut, WorkOrderCreate, WorkOrderUpdate,
    BulkStatusUpdate, SettingsOut, SettingsUpdate
)
from backend.detector import get_yolo_model, estimate_severity, simulate_gps, haversine, save_crop_snapshot

app = FastAPI(title="RoadSense API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, "static")
FRONTEND_DIST = os.path.join(ROOT_DIR, "static", "dist")
SAMPLES_DIR = os.path.join(ROOT_DIR, "samples")

os.makedirs(os.path.join(STATIC_DIR, "snapshots"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "proofs"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve generated sample images & video
if os.path.exists(SAMPLES_DIR):
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

job_state = {
    "is_processing": False,
    "progress": 0.0,
    "fps": 0.0,
    "total_frames": 0,
    "current_frame": 0,
    "detections_count": 0,
    "message": "Idle",
    "preview_frame": None,
    "completed": False
}

def calculate_priority_matrix(severity: str, lat: float) -> tuple[str, str, float]:
    """Automated Priority Matrix based on Severity + Traffic Corridor Simulation."""
    if severity == "High":
        priority = "Urgent"
        street = "Interstate Highway Corridor 101"
        cost = 450.0
    elif severity == "Medium":
        priority = "High"
        street = "Downtown Transit Avenue"
        cost = 250.0
    else:
        priority = "Low"
        street = "Residential Sector Road B"
        cost = 120.0
    return priority, street, cost

@app.get("/api/status")
def get_system_status(db: Session = Depends(get_db)):
    settings = db.query(SettingsModel).first()
    model_path = settings.model_path if settings else "models/best.pt"
    has_model = os.path.exists(model_path)
    return {
        "status": "online",
        "model_loaded": has_model,
        "model_path": model_path,
        "gpu_available": False
    }

@app.get("/api/settings", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    s = db.query(SettingsModel).first()
    if not s:
        s = SettingsModel()
        db.add(s)
        db.commit()
        db.refresh(s)
    
    has_model = os.path.exists(s.model_path)
    return SettingsOut(
        model_path=s.model_path,
        model_loaded=has_model,
        input_size=s.input_size,
        default_conf=s.default_conf,
        gps_mode=s.gps_mode,
        custom_gps_path=s.custom_gps_path
    )

@app.put("/api/settings", response_model=SettingsOut)
def update_settings(body: SettingsUpdate, db: Session = Depends(get_db)):
    s = db.query(SettingsModel).first()
    if body.model_path is not None:
        s.model_path = body.model_path
    if body.input_size is not None:
        s.input_size = body.input_size
    if body.default_conf is not None:
        s.default_conf = body.default_conf
    if body.gps_mode is not None:
        s.gps_mode = body.gps_mode
    db.commit()
    db.refresh(s)
    has_model = os.path.exists(s.model_path)
    return SettingsOut(
        model_path=s.model_path,
        model_loaded=has_model,
        input_size=s.input_size,
        default_conf=s.default_conf,
        gps_mode=s.gps_mode,
        custom_gps_path=s.custom_gps_path
    )

@app.delete("/api/data/clear")
def clear_demo_data(db: Session = Depends(get_db)):
    db.query(WorkOrder).delete()
    db.query(Detection).delete()
    db.commit()
    return {"message": "All detection records and work orders cleared successfully."}

@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_detections = db.query(Detection).count()
    high_sev = db.query(Detection).filter(Detection.severity == "High").count()
    dispatched = db.query(Detection).filter(Detection.status == "Dispatched").count()
    repaired = db.query(Detection).filter(Detection.status == "Repaired").count()
    
    # Calculate Total Saved Repair Budget Estimate
    repaired_items = db.query(WorkOrder).filter(WorkOrder.status == "Repaired").all()
    est_budget = sum([w.cost_estimate or 250.0 for w in repaired_items])
    
    return {
        "open_issues": total_detections - repaired,
        "high_severity": high_sev,
        "dispatched": dispatched,
        "repaired_this_week": repaired,
        "total_budget_allocated": round(est_budget, 2)
    }

@app.get("/api/detections/chart")
def get_detections_chart_data(db: Session = Depends(get_db)):
    all_dets = db.query(Detection).order_by(Detection.timestamp.asc()).all()
    date_counts = {}
    for d in all_dets:
        date_str = d.timestamp.strftime("%Y-%m-%d") if d.timestamp else "2026-10-07"
        if date_str not in date_counts:
            date_counts[date_str] = {"date": date_str, "Low": 0, "Medium": 0, "High": 0}
        date_counts[date_str][d.severity] += 1
    return list(date_counts.values())

@app.get("/api/detections", response_model=List[DetectionOut])
def list_detections(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Detection)
    if status and status != "All":
        query = query.filter(Detection.status == status)
    if severity and severity != "All":
        query = query.filter(Detection.severity == severity)
    if search:
        query = query.filter((Detection.code.ilike(f"%{search}%")) | (Detection.severity.ilike(f"%{search}%")))
    
    return query.order_by(Detection.timestamp.desc()).all()

@app.get("/api/detections/{detection_id}", response_model=DetectionOut)
def get_detection(detection_id: int, db: Session = Depends(get_db)):
    det = db.query(Detection).filter(Detection.id == detection_id).first()
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found")
    return det

@app.post("/api/detections/bulk-status")
def bulk_update_status(body: BulkStatusUpdate, db: Session = Depends(get_db)):
    db.query(Detection).filter(Detection.id.in_(body.ids)).update({"status": body.status}, synchronize_session=False)
    db.commit()
    return {"message": f"Updated {len(body.ids)} items to {body.status}"}

@app.post("/api/work-orders/{work_order_id}/proof")
def upload_repair_proof(
    work_order_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
        
    proof_dir = os.path.join(STATIC_DIR, "proofs")
    proof_filename = f"proof_wo_{work_order_id}_{int(time.time())}.jpg"
    proof_path = os.path.join(proof_dir, proof_filename)
    
    with open(proof_path, "wb") as f:
        f.write(file.file.read())
        
    url = f"/static/proofs/{proof_filename}"
    wo.repair_proof_path = url
    wo.status = "Repaired"
    
    det = db.query(Detection).filter(Detection.id == wo.detection_id).first()
    if det:
        det.status = "Repaired"
        det.repair_proof_path = url
        
    db.commit()
    return {"message": "Repair proof image uploaded and status updated to Repaired!", "proof_url": url}

@app.get("/api/detections/export/csv")
def export_csv(db: Session = Depends(get_db)):
    dets = db.query(Detection).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Code", "Timestamp", "Latitude", "Longitude", "Confidence", "Severity", "Priority", "Street_Corridor", "Status", "Simulated_GPS"])
    for d in dets:
        writer.writerow([d.id, d.code, d.timestamp, d.lat, d.lon, d.confidence, d.severity, d.priority, d.street_name, d.status, d.is_simulated_gps])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=roadsense_detections.csv"}
    )

@app.get("/api/work-orders", response_model=List[WorkOrderOut])
def list_work_orders(db: Session = Depends(get_db)):
    return db.query(WorkOrder).all()

@app.post("/api/work-orders", response_model=WorkOrderOut)
def create_work_order(body: WorkOrderCreate, db: Session = Depends(get_db)):
    det = db.query(Detection).filter(Detection.id == body.detection_id).first()
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    det.status = "Dispatched"
    title = body.title or f"Repair Pothole {det.code} on {det.street_name}"
    
    wo = WorkOrder(
        detection_id=det.id,
        title=title,
        assignee=body.assignee,
        priority=det.priority or "High",
        status="Dispatched",
        notes=body.notes or f"Geotagged at {det.lat:.5f}, {det.lon:.5f}. Street: {det.street_name}",
        cost_estimate=250.0 if det.severity == "Medium" else (450.0 if det.severity == "High" else 120.0)
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo

@app.patch("/api/work-orders/{work_order_id}", response_model=WorkOrderOut)
def update_work_order(work_order_id: int, body: WorkOrderUpdate, db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
        
    if body.status is not None:
        wo.status = body.status
        det = db.query(Detection).filter(Detection.id == wo.detection_id).first()
        if det:
            det.status = body.status
    if body.assignee is not None:
        wo.assignee = body.assignee
    if body.priority is not None:
        wo.priority = body.priority
    if body.notes is not None:
        wo.notes = body.notes
        
    wo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(wo)
    return wo

def run_video_processing(file_path: str, conf_threshold: float, db: Session):
    global job_state
    job_state["is_processing"] = True
    job_state["progress"] = 0.0
    job_state["completed"] = False
    job_state["detections_count"] = 0
    job_state["message"] = "Processing video stream..."

    model, loaded, info = get_yolo_model()
    cap = cv2.VideoCapture(file_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    job_state["total_frames"] = total_frames
    
    frame_idx = 0
    recent_detections = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_idx += 1
        t0 = time.time()
        
        resized = cv2.resize(frame, (640, 640))
        
        if model is not None:
            results = model(resized, conf=conf_threshold, verbose=False)[0]
            
            elapsed_sec = frame_idx / fps
            lat, lon = simulate_gps(elapsed_sec)
            
            for box in results.boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                severity, _ = estimate_severity(xyxy, (640, 640))
                
                is_dup = False
                for prev_lat, prev_lon, prev_t in recent_detections:
                    if abs(elapsed_sec - prev_t) < 4.0 and haversine(lat, lon, prev_lat, prev_lon) < 5.0:
                        is_dup = True
                        break
                        
                if not is_dup:
                    snapshot_url = save_crop_snapshot(resized, xyxy)
                    code_idx = db.query(Detection).count() + 1
                    code = f"PTH-{code_idx:04d}"
                    priority, street, _ = calculate_priority_matrix(severity, lat)
                    
                    det = Detection(
                        code=code,
                        timestamp=datetime.utcnow(),
                        lat=round(lat, 6),
                        lon=round(lon, 6),
                        confidence=round(conf, 2),
                        severity=severity,
                        priority=priority,
                        street_name=street,
                        status="Reported",
                        snapshot_path=snapshot_url,
                        is_simulated_gps=True
                    )
                    db.add(det)
                    db.commit()
                    
                    recent_detections.append((lat, lon, elapsed_sec))
                    job_state["detections_count"] += 1

        proc_time = time.time() - t0
        job_state["fps"] = round(1.0 / proc_time, 1) if proc_time > 0 else 30.0
        job_state["current_frame"] = frame_idx
        job_state["progress"] = min(1.0, frame_idx / total_frames)
        
    cap.release()
    try:
        os.remove(file_path)
    except Exception:
        pass
        
    job_state["is_processing"] = False
    job_state["progress"] = 1.0
    job_state["completed"] = True
    job_state["message"] = "Analysis completed!"

@app.post("/api/analyze/upload")
def upload_media_for_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conf_threshold: float = Form(0.25),
    db: Session = Depends(get_db)
):
    global job_state
    if job_state["is_processing"]:
        raise HTTPException(status_code=400, detail="Analysis already in progress")
        
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        f.write(file.file.read())
        
    is_image = file.filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'png']
    
    if is_image:
        frame = cv2.imread(temp_path)
        if frame is not None:
            model, _, _ = get_yolo_model()
            resized = cv2.resize(frame, (640, 640))
            results = model(resized, conf=conf_threshold, verbose=False)[0] if model else None
            
            count = 0
            if results:
                for box in results.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    severity, _ = estimate_severity(xyxy, (640, 640))
                    snapshot_url = save_crop_snapshot(resized, xyxy)
                    
                    code_idx = db.query(Detection).count() + 1
                    code = f"PTH-{code_idx:04d}"
                    priority, street, _ = calculate_priority_matrix(severity, 37.7749)
                    
                    det = Detection(
                        code=code,
                        timestamp=datetime.utcnow(),
                        lat=37.7749,
                        lon=-122.4194,
                        confidence=round(conf, 2),
                        severity=severity,
                        priority=priority,
                        street_name=street,
                        status="Reported",
                        snapshot_path=snapshot_url,
                        is_simulated_gps=True
                    )
                    db.add(det)
                    db.commit()
                    count += 1
                    
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
            return {
                "status": "completed",
                "message": f"Processed image successfully. Found {count} defect(s).",
                "detections_count": count
            }
    else:
        background_tasks.add_task(run_video_processing, temp_path, conf_threshold, db)
        return {"status": "started", "message": "Video analysis job launched."}

@app.get("/api/analyze/job-status")
def get_job_status():
    global job_state
    return job_state

# ---------------------------------------------------------------------------
# Serve the React SPA build (output of: cd frontend && npm run build)
# Vite is configured to build into static/dist/
# ---------------------------------------------------------------------------
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "dist")

if os.path.exists(FRONTEND_DIST):
    # Serve Vite-generated assets (JS/CSS bundles)
    _assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="frontend_assets")

    @app.get("/")
    def serve_root():
        """Serve React SPA index at root."""
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """SPA catch-all: return index.html for any non-API route."""
        # Don't intercept API or static asset routes
        for prefix in ("api", "static", "samples", "assets"):
            if full_path.startswith(prefix):
                raise HTTPException(status_code=404, detail="Not found")
        # Try to serve exact file (favicons, manifest, etc.)
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise fall back to SPA index
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
else:
    @app.get("/")
    def serve_root_no_build():
        """Friendly message when the React app hasn't been built yet."""
        return {
            "message": "RoadSense API is running. React frontend not built yet.",
            "hint": "Run: cd frontend && npm run build",
            "api_docs": "/docs"
        }

