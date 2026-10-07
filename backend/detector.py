import os
import cv2
import time
import math
import uuid
import numpy as np
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best.pt")
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

_model_cache = None

def get_yolo_model(path=None):
    global _model_cache
    target_path = path or MODEL_PATH
    if not os.path.exists(target_path):
        # Fallback to yolov8n.pt if best.pt is not present yet
        target_path = "yolov8n.pt"

    try:
        from ultralytics import YOLO
        model = YOLO(target_path)
        return model, True, target_path
    except Exception as e:
        return None, False, str(e)

def is_model_loaded(path=None):
    target_path = path or MODEL_PATH
    return os.path.exists(target_path) or os.path.exists("yolov8n.pt")

def estimate_severity(box, frame_shape):
    x1, y1, x2, y2 = box
    box_area = (x2 - x1) * (y2 - y1)
    frame_area = frame_shape[0] * frame_shape[1]
    ratio = box_area / frame_area if frame_area > 0 else 0
    
    if ratio < 0.015:
        return "Low", ratio
    elif ratio < 0.05:
        return "Medium", ratio
    else:
        return "High", ratio

def simulate_gps(elapsed_seconds, start_lat=37.7749, start_lon=-122.4194, speed_kmh=30.0):
    speed_ms = speed_kmh / 3.6
    dist = speed_ms * elapsed_seconds
    lat_off = (dist * 0.7071) / 111000.0
    lon_off = (dist * 0.7071) / (111000.0 * math.cos(math.radians(start_lat)))
    return start_lat + lat_off, start_lon + lon_off

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def save_crop_snapshot(frame, box):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = map(int, box)
    # Pad box by 10% for context
    pad_w = int((x2 - x1) * 0.1)
    pad_h = int((y2 - y1) * 0.1)
    cx1 = max(0, x1 - pad_w)
    cy1 = max(0, y1 - pad_h)
    cx2 = min(w, x2 + pad_w)
    cy2 = min(h, y2 + pad_h)
    
    crop = frame[cy1:cy2, cx1:cx2]
    if crop.size == 0:
        crop = frame
        
    filename = f"snap_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    cv2.imwrite(filepath, crop)
    return f"/static/snapshots/{filename}"
