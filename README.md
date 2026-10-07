# 🛣️ RoadSense — City Road Condition Monitoring Platform

**RoadSense** is an enterprise-grade municipal road-condition monitoring platform designed for city road departments. It detects potholes and road damage in dashcam video using fine-tuned YOLOv8, tags detections with spatial GPS telemetry, and automates work order repair dispatch.

---

## 🏗️ Architecture & Stack

- **Backend**: FastAPI + Ultralytics YOLOv8 + OpenCV + SQLite (SQLAlchemy).
- **Frontend**: React + Vite + TypeScript + Tailwind CSS + Leaflet (`react-leaflet`) + Recharts.
- **Serving**: Production React bundle compiled and served directly via FastAPI static mounts.

---

## ⚡ Quick Start

### 1. Installation
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run RoadSense Product
Execute the unified single-command runner:
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open your browser at:  
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📁 Project Structure

```
pothole_detection_yolov8/
├── backend/
│   ├── main.py            # FastAPI endpoints & static frontend serving
│   ├── database.py        # SQLite SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic data schemas
│   └── detector.py        # YOLOv8 inference, crop snapshots & GPS logic
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navigation.tsx     # TopBar & Sidebar
│   │   │   ├── Dashboard.tsx      # KPI cards, Leaflet map & frequency chart
│   │   │   ├── Analyze.tsx        # Drag-and-drop video/image background processing
│   │   │   ├── Issues.tsx         # Searchable, filterable table & bulk dispatch
│   │   │   ├── WorkOrders.tsx     # Kanban board (Reported, Dispatched, In progress, Repaired)
│   │   │   ├── SettingsView.tsx   # Model path, GPS mode & data management
│   │   │   └── DetailDrawer.tsx   # Incident crop snapshot slideout drawer
│   │   ├── App.tsx
│   │   └── types.ts
│   └── dist/              # Built frontend bundle
│
├── models/
│   └── best.pt            # YOLOv8 model weights
├── static/
│   └── snapshots/         # Auto-saved cropped defect images
├── requirements.txt
└── README.md
```
