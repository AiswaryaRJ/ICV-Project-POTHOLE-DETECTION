import os
import time
import cv2
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best.pt")

def load_yolo_model():
    if not os.path.exists(MODEL_PATH):
        try:
            from ultralytics import YOLO
            # Fallback to standard pretrained YOLOv8 model for seamless demonstration
            model = YOLO("yolov8n.pt")
            return model, "Fine-tuned 'best.pt' not found in models/. Running in Demo Mode with standard YOLOv8 weights."
        except Exception as e:
            return None, f"Model file not found at '{MODEL_PATH}'. Error loading fallback model: {str(e)}"
    try:
        from ultralytics import YOLO
        model = YOLO(MODEL_PATH)
        return model, None
    except Exception as e:
        return None, f"Error loading model: {str(e)}"

def estimate_severity(box, frame_shape):
    """
    Rough 2D area estimate relative to frame size.
    box: [x1, y1, x2, y2]
    """
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

def process_frame(model, frame, conf_threshold=0.25):
    """
    Processes a single frame: resizes to 640x640, normalizes (handled by YOLO internal pipeline),
    runs inference, draws boxes & severity tags.
    Returns: annotated_frame, detections list
    """
    h, w = frame.shape[:2]
    # Resize frame to standard 640x640 for consistency
    resized_frame = cv2.resize(frame, (640, 640))
    
    # Run YOLOv8 inference
    results = model(resized_frame, conf=conf_threshold, verbose=False)[0]
    
    detections = []
    annotated = resized_frame.copy()
    
    for box in results.boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0].cpu().numpy())
        cls_id = int(box.cls[0].cpu().numpy())
        
        severity, ratio = estimate_severity(xyxy, resized_frame.shape)
        
        x1, y1, x2, y2 = map(int, xyxy)
        
        # Color coding by severity
        if severity == "Low":
            color = (0, 255, 0)     # Green
        elif severity == "Medium":
            color = (0, 165, 255)   # Amber/Orange
        else:
            color = (0, 0, 255)     # Red
            
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f"Pothole {conf:.2f} | {severity}"
        cv2.putText(annotated, label, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        detections.append({
            "bbox": [x1, y1, x2, y2],
            "confidence": conf,
            "severity": severity,
            "area_ratio": ratio
        })
        
    # Resize annotated frame back to original aspect ratio display if desired, or return 640x640
    return annotated, detections
