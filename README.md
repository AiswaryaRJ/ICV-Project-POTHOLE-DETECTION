# RoadSense — Pothole & Road Damage Detection System

A full-stack smart city road infrastructure system. Citizens report potholes via dashcam footage; government operators manage, dispatch, and resolve incidents through a real-time dashboard.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  React + TypeScript Frontend (CityHub)  │  ← localhost:8000/
│  Citizen upload + Government dashboard  │
└────────────────┬────────────────────────┘
                 │ /api/*
┌────────────────▼────────────────────────┐
│  FastAPI Backend (RoadSense API)         │  ← localhost:8000
│  YOLOv8 inference · SQLite · REST API   │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start (One Command)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (first time only)
cd frontend && npm install && cd ..

# Launch everything — builds React, starts server, opens browser
python start.py
```

Then open **http://localhost:8000** 🎉

---

## 👤 User Roles

### Citizen View
- Upload dashcam images or video
- Automatic pothole detection via YOLOv8
- GPS geotagging of detected incidents
- Real-time processing progress
- View report confirmation

### Government / Admin View (CityHub Dashboard)
- Live incident map with severity heatmap
- Incident reports with photo evidence & location
- Work order management & technician dispatch
- Analytics: detection trends, severity breakdown, repair costs
- Status workflow: Reported → Dispatched → In Progress → Repaired

---

## 📁 Project Structure

```
pothole_detection_yolov8/
├── backend/
│   ├── main.py          # FastAPI app (serves API + React SPA)
│   ├── database.py      # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── detector.py      # YOLOv8 inference engine
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Analyze.tsx     # Citizen upload & detection
│       │   ├── Dashboard.tsx   # Admin map & metrics
│       │   ├── Issues.tsx      # Incident list & review
│       │   ├── WorkOrders.tsx  # Dispatch management
│       │   └── SettingsView.tsx
│       └── App.tsx
├── samples/
│   ├── images/          # 5 demo pothole images
│   └── videos/          # 20s simulated dashcam video
├── models/              # Place best.pt here
├── static/
│   └── dist/            # Built React app (served by FastAPI)
├── start.py             # ← One-command launcher
├── migrate_db.py        # DB schema migration helper
└── requirements.txt
```

---

## 🤖 Model Setup

Place your fine-tuned YOLOv8 weights at:
```
models/best.pt
```

If `best.pt` is not present, the system runs in **demo mode** using YOLOv8n base weights.

---

## 🧪 Sample Demo Media

Built-in sample pothole images and a 20-second dashcam video are included in `samples/`.
Use them in the **Analyze** tab without needing real footage.

---

## 📦 Dependencies

```bash
pip install fastapi uvicorn sqlalchemy ultralytics opencv-python pillow python-multipart
```

---

## 🌐 API Docs

FastAPI auto-generates interactive API documentation at:
- **http://localhost:8000/docs** (Swagger UI)
- **http://localhost:8000/redoc** (ReDoc)
