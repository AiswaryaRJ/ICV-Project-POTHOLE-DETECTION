import os
import math
import pandas as pd
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "detections.csv")

COLUMNS = ["id", "timestamp", "lat", "lon", "confidence", "severity", "status"]

def ensure_data_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_FILE, index=False)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two lat/lon points."""
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def load_detections():
    ensure_data_file()
    try:
        df = pd.read_csv(DATA_FILE)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def is_duplicate(lat, lon, timestamp, dist_threshold_m=5.0, time_threshold_s=3.0):
    df = load_detections()
    if df.empty:
        return False
    
    for _, row in df.iterrows():
        try:
            prev_lat = float(row['lat'])
            prev_lon = float(row['lon'])
            dist = haversine_distance(lat, lon, prev_lat, prev_lon)
            
            # Simple timestamp check if available in ISO format or timestamp string
            # Here timestamp passed to function is elapsed seconds or datetime string
            # We enforce distance check primarily
            if dist < dist_threshold_m:
                return True
        except Exception:
            continue
    return False

def save_detection(lat, lon, confidence, severity, status="Reported", timestamp_str=None):
    ensure_data_file()
    if timestamp_str is None:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    if is_duplicate(lat, lon, timestamp_str):
        return None  # Skipped duplicate
        
    df = load_detections()
    new_id = f"PTH-{len(df) + 1:04d}"
    
    new_row = {
        "id": new_id,
        "timestamp": timestamp_str,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "confidence": round(float(confidence), 2),
        "severity": severity,
        "status": status
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=False)
    df.to_csv(DATA_FILE, index=False)
    return new_row

def update_detection_status(detection_id, new_status):
    ensure_data_file()
    df = load_detections()
    if not df.empty and "id" in df.columns:
        df.loc[df["id"] == detection_id, "status"] = new_status
        df.to_csv(DATA_FILE, index=False)
        return True
    return False
