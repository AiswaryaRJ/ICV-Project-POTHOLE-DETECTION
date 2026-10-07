import os
from ultralytics import YOLO

os.makedirs("models", exist_ok=True)
m = YOLO("yolov8n.pt")
m.save("models/best.pt")
print("Saved models/best.pt successfully!")
