import os
import time
import tempfile
import cv2
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import streamlit as st
import folium
from streamlit_folium import st_folium

from detector import load_yolo_model, process_frame
from gps import get_gps_for_frame
from store import load_detections, save_detection, update_detection_status

# ---- SAMPLE MEDIA PATHS ----
SAMPLES_DIR = Path(__file__).parent.parent / "samples"
SAMPLE_IMAGES_DIR = SAMPLES_DIR / "images"
SAMPLE_VIDEO_PATH = SAMPLES_DIR / "videos" / "sample_dashcam.mp4"

SAMPLE_IMAGE_META = {
    "pothole_daytime_large.png":      {"label": "Large Pothole (Day)",       "icon": "☀️",  "severity": "High"},
    "pothole_multiple_cracks.png":    {"label": "Multiple Cracks (Overcast)","icon": "🌥️", "severity": "High"},
    "pothole_nighttime_rain.png":     {"label": "Rain-Filled Pothole (Night)","icon": "🌧️", "severity": "Medium"},
    "pothole_highway_damage.png":     {"label": "Highway Road Damage",        "icon": "🛣️", "severity": "Medium"},
    "pothole_intersection_severe.png":{"label": "Severe Intersection Damage", "icon": "🚦", "severity": "High"},
}

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RoadPulse - Smart City Pothole & Infrastructure Intelligence",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN HIGH-END CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sleek Modern Dark Theme */
    .stApp {
        background: #090d16;
        color: #e2e8f0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #111827 !important;
        border-right: 1px solid #1f2937;
    }
    
    /* Main Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        max-width: 800px;
        line-height: 1.6;
    }

    /* Glassmorphism Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        text-align: left;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(249, 115, 22, 0.4);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f97316;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    /* Pipeline Step Box */
    .pipeline-step {
        background: #1e293b;
        border-top: 3px solid #f97316;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        height: 100%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .pipeline-step h5 {
        color: #f8fafc;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .pipeline-step p {
        color: #94a3b8;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* Planned Feature Cards */
    .planned-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 18px;
        position: relative;
    }
    .badge-planned {
        background: rgba(249, 115, 22, 0.15);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.3);
        padding: 4px 10px;
        font-size: 0.72rem;
        font-weight: 700;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Alert Customization */
    .stAlert {
        border-radius: 10px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #ea580c 0%, #f97316 100%);
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 6px 16px rgba(234, 88, 12, 0.4);
        transform: translateY(-1px);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.82rem;
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### 🚘 RoadPulse AI")
st.sidebar.caption("Smart City Road Damage & Telemetry System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation Menu",
    ["Overview", "Live Detection", "Municipal Command Center", "Model Performance", "Future Innovations"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size: 0.8rem; color: #64748b; padding: 10px; background: #1e293b; border-radius: 8px;">
    <b>Deployment Target:</b> NVIDIA Jetson Edge<br>
    <b>Model Architecture:</b> YOLOv8 Fine-Tuned<br>
    <b>Telemetry Sync:</b> Active
</div>
""", unsafe_allow_html=True)

# --- PAGE 1: OVERVIEW ---
if page == "Overview":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Automated Pothole & Road Hazard Intelligence</div>
        <div class="hero-subtitle">
            Empowering smart cities with real-time computer vision from dashcam footage. Automatically detect, 
            geotag, and dispatch repairs for urban road degradation before accidents happen.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔄 End-to-End System Pipeline")
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.markdown("<div class='pipeline-step'><h5>1. Dashcam Feed</h5><p>Real-time video input from civic or public transit vehicles</p></div>", unsafe_allow_html=True)
    with p2:
        st.markdown("<div class='pipeline-step'><h5>2. Preprocess</h5><p>Frame extraction, 640x640 resize & dynamic scaling</p></div>", unsafe_allow_html=True)
    with p3:
        st.markdown("<div class='pipeline-step'><h5>3. YOLOv8 Inference</h5><p>Edge object detection with severity estimation</p></div>", unsafe_allow_html=True)
    with p4:
        st.markdown("<div class='pipeline-step'><h5>4. GPS Geotagging</h5><p>Spatial coordinate assignment per frame timestamp</p></div>", unsafe_allow_html=True)
    with p5:
        st.markdown("<div class='pipeline-step'><h5>5. Dispatch Hub</h5><p>Automated database log & municipal repair dispatch</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✨ Platform Features for Citizens & Municipalities")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.5rem;">⚡</div>
            <div style="font-weight:600; color:#f8fafc; margin-top:8px;">Edge Computing Ready</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:6px;">Designed to run at high FPS on embedded hardware like NVIDIA Jetson Orin with minimal energy consumption.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.5rem;">📍</div>
            <div style="font-weight:600; color:#f8fafc; margin-top:8px;">Geospatial Telemetry</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:6px;">Pairs computer vision bounding boxes with simulated or live GPS telemetry to accurately pinpoint road defects.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:1.5rem;">🛠️</div>
            <div style="font-weight:600; color:#f8fafc; margin-top:8px;">Automated Repair Dispatch</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:6px;">Deduplicates repeated detections and streams verified incidents directly into municipal work-order queues.</div>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 2: LIVE DETECTION ---
elif page == "Live Detection":
    st.markdown("## 🔍 Real-Time Defect Detection")
    st.caption("Upload dashcam video or images to run instant computer vision inference & geotagging.")
    
    model, status_msg = load_yolo_model()
    if status_msg:
        if "Demo Mode" in status_msg:
            st.info(f"ℹ️ **Notice:** {status_msg}")
        else:
            st.warning(f"⚠️ {status_msg}")
            
    col_ctrl, col_view = st.columns([1, 2])
    
    with col_ctrl:
        st.markdown("#### ⚙️ Detection Settings")
        conf_thresh = st.slider("Model Confidence Threshold", 0.05, 1.0, 0.25, 0.05)
        
        st.markdown("#### 📡 Telemetry Simulation")
        start_lat = st.number_input("Vehicle Start Latitude", value=37.7749, format="%.4f")
        start_lon = st.number_input("Vehicle Start Longitude", value=-122.4194, format="%.4f")
        vehicle_speed = st.slider("Vehicle Speed (km/h)", 10, 100, 30)
        
        custom_gps_file = st.file_uploader("Upload GPS Log CSV (Optional)", type=["csv"])
        custom_gps_df = None
        if custom_gps_file:
            try:
                custom_gps_df = pd.read_csv(custom_gps_file)
                st.success("Loaded custom GPS track.")
            except Exception as e:
                st.error(f"Failed to read CSV: {e}")
                
        st.info("📌 **Note:** GPS coordinates are assigned dynamically per frame. You can override with a custom CSV track.")

        st.markdown("---")
        st.markdown("#### 🖼️ Sample Media Library")
        st.caption("Use built-in demo assets — no upload needed!")

        sample_file_path = None  # will be set if user picks a sample

        # --- Sample Images ---
        available_samples = []
        if SAMPLE_IMAGES_DIR.exists():
            available_samples = [f for f in sorted(SAMPLE_IMAGES_DIR.glob("*.png")) if f.name in SAMPLE_IMAGE_META]

        if available_samples:
            # Render thumbnail grid (2 columns)
            thumb_cols = st.columns(2)
            for i, img_path in enumerate(available_samples):
                meta = SAMPLE_IMAGE_META[img_path.name]
                with thumb_cols[i % 2]:
                    try:
                        pil_thumb = Image.open(img_path)
                        pil_thumb.thumbnail((300, 200))
                        st.image(pil_thumb, use_container_width=True)
                    except Exception:
                        pass
                    if st.button(
                        f"{meta['icon']} {meta['label']}",
                        key=f"sample_img_{img_path.stem}",
                        use_container_width=True,
                    ):
                        st.session_state["sample_file_path"] = str(img_path)
                        st.session_state["sample_type"] = "image"
                        st.toast(f"Loaded: {meta['label']}", icon=meta['icon'])

        # --- Sample Video ---
        st.markdown("")
        if SAMPLE_VIDEO_PATH.exists():
            if st.button("🎬 Load Demo Dashcam Video (20s)", use_container_width=True):
                st.session_state["sample_file_path"] = str(SAMPLE_VIDEO_PATH)
                st.session_state["sample_type"] = "video"
                st.toast("Loaded: Sample Dashcam Video", icon="🎬")

        # Resolve active sample
        if "sample_file_path" in st.session_state and st.session_state["sample_file_path"]:
            sample_file_path = st.session_state["sample_file_path"]
            sample_type = st.session_state.get("sample_type", "image")
            st.success(f"Sample ready: `{Path(sample_file_path).name}` — press **Start Detection** to run.")

        if st.button("✖ Clear Sample", key="clear_sample"):
            st.session_state.pop("sample_file_path", None)
            st.session_state.pop("sample_type", None)
            sample_file_path = None

        st.markdown("---")
        st.markdown("#### 📤 Or Upload Your Own")
        uploaded_file = st.file_uploader("Upload Dashcam Media", type=["mp4", "avi", "mov", "jpg", "jpeg", "png"])
        run_btn = st.button("🚀 Start Detection Pipeline", use_container_width=True)

    with col_view:
        st.markdown("#### 🎥 Live Inference Output")

        # Resolve active media: uploaded file takes priority over sample
        active_path = None
        active_is_image = False
        active_label = None

        if uploaded_file:
            active_label = uploaded_file.name
            active_is_image = uploaded_file.name.split('.')[-1].lower() in ['jpg', 'jpeg', 'png']
        elif sample_file_path and Path(sample_file_path).exists():
            active_path = sample_file_path
            active_label = Path(sample_file_path).name
            active_is_image = st.session_state.get("sample_type", "image") == "image"

        # Preview sample before running
        if active_path and not uploaded_file:
            if active_is_image:
                st.image(active_path, caption=f"Preview: {active_label}", use_container_width=True)
            else:
                st.video(active_path)
                st.caption(f"Preview: {active_label} — press Start Detection to run inference")

        if (uploaded_file or active_path) and run_btn:
            if model is None:
                st.error("Model engine is unavailable.")
            else:
                if active_is_image:
                    if uploaded_file:
                        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                        image = cv2.imdecode(file_bytes, 1)
                    else:
                        image = cv2.imread(active_path)

                    t0 = time.time()
                    annotated, detections = process_frame(model, image, conf_thresh)
                    latency = (time.time() - t0) * 1000
                    fps = 1000.0 / latency if latency > 0 else 0

                    lat, lon, is_sim = get_gps_for_frame(0, 30, start_lat, start_lon, vehicle_speed, custom_gps_df)

                    st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)
                    st.success(f"Processed image in **{latency:.1f} ms** (~**{fps:.1f} FPS**)")

                    # Detection results table
                    if detections:
                        det_df = pd.DataFrame(detections)
                        st.dataframe(
                            det_df[["severity", "confidence"]].rename(columns={"severity": "Severity", "confidence": "Confidence"}),
                            use_container_width=True,
                            hide_index=True,
                        )

                    saved_count = 0
                    for d in detections:
                        res = save_detection(lat, lon, d["confidence"], d["severity"])
                        if res:
                            saved_count += 1
                    if saved_count > 0:
                        st.balloons()
                        st.info(f"Logged **{saved_count}** defect(s) to Municipal Storage.")

                else:
                    # Video processing
                    if uploaded_file:
                        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                        tfile.write(uploaded_file.read())
                        video_source = tfile.name
                    else:
                        video_source = active_path

                    cap = cv2.VideoCapture(video_source)
                    video_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
                    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                    st_frame = st.empty()
                    st_metrics = st.empty()
                    progress_bar = st.progress(0, text="Processing video...")

                    frame_idx = 0
                    total_detections_logged = 0

                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break

                        frame_idx += 1
                        t0 = time.time()
                        annotated, detections = process_frame(model, frame, conf_thresh)
                        proc_time = time.time() - t0
                        current_fps = 1.0 / proc_time if proc_time > 0 else 0

                        lat, lon, is_sim = get_gps_for_frame(frame_idx, video_fps, start_lat, start_lon, vehicle_speed, custom_gps_df)

                        for d in detections:
                            res = save_detection(lat, lon, d["confidence"], d["severity"])
                            if res:
                                total_detections_logged += 1

                        st_frame.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)
                        gps_tag = "Simulated Track" if is_sim else "Custom CSV Track"
                        st_metrics.markdown(
                            f"⚡ **FPS:** `{current_fps:.1f}` | 📍 `{lat:.5f}, {lon:.5f}` ({gps_tag}) | 📝 Logged: `{total_detections_logged}`"
                        )

                        if total_video_frames > 0:
                            progress_bar.progress(
                                min(frame_idx / total_video_frames, 1.0),
                                text=f"Frame {frame_idx}/{total_video_frames}"
                            )

                    cap.release()
                    progress_bar.progress(1.0, text="Complete!")
                    st.success(f"Video processing complete! Logged **{total_detections_logged}** detections.")

# --- PAGE 3: MUNICIPAL COMMAND CENTER ---
elif page == "Municipal Command Center":
    st.markdown("## 🏛️ Municipal Repair Command Center")
    st.caption("City-wide road health overview, automated defect geotagging, and dispatch workflow.")
    
    df = load_detections()
    
    total_potholes = len(df)
    high_sev = len(df[df["severity"] == "High"]) if not df.empty else 0
    dispatched = len(df[df["status"] == "Dispatched"]) if not df.empty else 0
    repaired = len(df[df["status"] == "Repaired"]) if not df.empty else 0
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Reported</div><div class='metric-value'>{total_potholes}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>High Severity</div><div class='metric-value' style='color:#ef4444;'>{high_sev}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Work Orders Sent</div><div class='metric-value' style='color:#3b82f6;'>{dispatched}</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Potholes Fixed</div><div class='metric-value' style='color:#22c55e;'>{repaired}</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 📍 Live Incident Map")
    if df.empty:
        st.info("No road defects recorded yet. Run live detection to stream data to this dashboard.")
        m = folium.Map(location=[37.7749, -122.4194], zoom_start=14, tiles="OpenStreetMap")
        st_folium(m, width=1100, height=420)
    else:
        avg_lat = df["lat"].mean()
        avg_lon = df["lon"].mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14, tiles="OpenStreetMap")
        
        for _, row in df.iterrows():
            sev = row["severity"]
            color = "green" if sev == "Low" else "orange" if sev == "Medium" else "red"
            popup_txt = f"<b>Defect ID:</b> {row['id']}<br><b>Severity:</b> {sev}<br><b>Conf:</b> {row['confidence']}<br><b>Status:</b> {row['status']}"
            
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=8,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                popup=popup_txt
            ).add_to(m)
            
        st_folium(m, width=1100, height=420)

    st.markdown("### 📋 Repair Dispatch Queue")
    if not df.empty:
        for idx, row in df.iterrows():
            c_id, c_time, c_coords, c_sev, c_conf, c_stat, c_b1, c_b2 = st.columns([1, 1.5, 1.5, 1, 1, 1, 1.2, 1.2])
            
            c_id.markdown(f"**{row['id']}**")
            c_time.write(row['timestamp'])
            c_coords.write(f"{row['lat']:.4f}, {row['lon']:.4f}")
            
            sev = row['severity']
            sev_color = "#22c55e" if sev == "Low" else "#f97316" if sev == "Medium" else "#ef4444"
            c_sev.markdown(f"<span style='color:{sev_color}; font-weight:700;'>{sev}</span>", unsafe_allow_html=True)
            
            c_conf.write(f"{row['confidence']:.2f}")
            c_stat.markdown(f"`{row['status']}`")
            
            if c_b1.button("🚚 Dispatch", key=f"disp_{row['id']}"):
                update_detection_status(row['id'], "Dispatched")
                st.rerun()
                
            if c_b2.button("✅ Fixed", key=f"rep_{row['id']}"):
                update_detection_status(row['id'], "Repaired")
                st.rerun()
    else:
        st.write("No active incidents logged in database.")

# --- PAGE 4: MODEL PERFORMANCE ---
elif page == "Model Performance":
    st.markdown("## 📊 Model Evaluation & Metrics")
    st.caption("Fine-tuned YOLOv8 evaluation metrics and training artifacts.")
    
    st.markdown("#### 🎯 Quantitative Results")
    st.write("Enter your verified evaluation results below:")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.text_input("mAP@50", value="", placeholder="e.g. 0.842")
    with m2:
        st.text_input("Precision", value="", placeholder="e.g. 0.815")
    with m3:
        st.text_input("Recall", value="", placeholder="e.g. 0.789")
        
    st.markdown("---")
    st.markdown("#### 📈 Training Artifacts")
    
    runs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "runs", "detect", "train")
    results_img_path = os.path.join(runs_dir, "results.png")
    cm_img_path = os.path.join(runs_dir, "confusion_matrix.png")
    
    has_artifacts = False
    if os.path.exists(results_img_path):
        st.image(results_img_path, caption="Training & Validation Curves (runs/detect/train/results.png)", use_container_width=True)
        has_artifacts = True
    if os.path.exists(cm_img_path):
        st.image(cm_img_path, caption="Confusion Matrix (runs/detect/train/confusion_matrix.png)", use_container_width=True)
        has_artifacts = True
        
    if not has_artifacts:
        st.info("ℹ️ **Notice:** No training output images found in `runs/detect/train/`. Copy your `results.png` or `confusion_matrix.png` there to display them.")

# --- PAGE 5: FUTURE INNOVATIONS ---
elif page == "Future Innovations":
    st.markdown("## 🚀 Future Technical Roadmap")
    st.caption("Next-generation smart city infrastructure monitoring innovations.")
    
    st.markdown("""
    <div class="planned-card">
        <span class="badge-planned">PLANNED</span>
        <h3 style="color:#f8fafc; margin-top:10px;">1. 3D Volumetric Depth Sensing</h3>
        <p style="color:#94a3b8; font-size:0.92rem;">
            Integration with stereoscopic depth cameras (e.g. Intel RealSense, Ouster LiDAR) to estimate 
            pothole depth and volume ($m^3$). This provides municipal engineering teams with exact asphalt repair quantity estimates prior to crew dispatch.
        </p>
    </div>
    
    <div class="planned-card">
        <span class="badge-planned">PLANNED</span>
        <h3 style="color:#f8fafc; margin-top:10px;">2. NVIDIA Jetson Edge Acceleration</h3>
        <p style="color:#94a3b8; font-size:0.92rem;">
            Exporting fine-tuned models to INT8 TensorRT engines for deployment on embedded edge hardware 
            (NVIDIA Jetson Orin Nano / Xavier NX), allowing real-time processing directly on civic vehicles with sub-15ms frame latency.
        </p>
    </div>
    
    <div class="planned-card">
        <span class="badge-planned">PLANNED</span>
        <h3 style="color:#f8fafc; margin-top:10px;">3. Transit Bus Fleet Heatmaps</h3>
        <p style="color:#94a3b8; font-size:0.92rem;">
            Mounting vision sensors across municipal bus fleets to continuously audit city roads. Aggregated telemetry builds 
            predictive road health heatmaps to repair micro-cracks before severe potholes form.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    🚘 <b>RoadPulse</b> — Real-Time Pothole Detection & Smart City Infrastructure Intelligence Framework
</div>
""", unsafe_allow_html=True)
