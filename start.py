"""
start.py  —  RoadSense One-Command Launcher
============================================
Starts the FastAPI backend (port 8000) which also serves the pre-built
React frontend at http://localhost:8000/.

Usage:
    python start.py

What it does:
  1. Builds the React frontend (cd frontend && npm run build) if not already built
  2. Starts the FastAPI backend with uvicorn on port 8000
  3. Opens http://localhost:8000 in your browser automatically

Roles:
  - Citizen  → Upload dashcam footage / images, report potholes
  - Admin    → Government dashboard: incidents, work orders, analytics
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontend"
DIST_DIR = ROOT / "static" / "dist"


def build_frontend():
    """Run npm run build in the frontend directory."""
    print("\n[1/2] Building React frontend...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(FRONTEND_DIR),
        shell=True,
    )
    if result.returncode != 0:
        print("\n[ERROR] Frontend build failed. Check npm/node installation.")
        sys.exit(1)
    print("[1/2] Frontend build complete.")


def open_browser_after_delay(url: str, delay: float = 2.5):
    """Open the browser after a short delay to let uvicorn start."""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def start_backend():
    """Start the FastAPI backend with uvicorn."""
    print("\n[2/2] Starting FastAPI backend on http://localhost:8000 ...")
    print("      Press Ctrl+C to stop.\n")
    open_browser_after_delay("http://localhost:8000")
    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ],
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    # Always rebuild if dist is missing; otherwise ask
    if not DIST_DIR.exists() or not any(DIST_DIR.iterdir()):
        build_frontend()
    else:
        answer = input(
            f"\nFrontend build found at {DIST_DIR}.\n"
            "Rebuild? [y/N]: "
        ).strip().lower()
        if answer == "y":
            build_frontend()
        else:
            print("[1/2] Skipping rebuild (using existing build).")

    start_backend()
