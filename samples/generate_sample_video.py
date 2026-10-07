"""
generate_sample_video.py
------------------------
Generates a realistic simulated dashcam video from the sample pothole images.
Each image is displayed for several frames with subtle camera shake and zoom
to mimic actual dashcam footage motion.

Usage:
    python samples/generate_sample_video.py

Output:
    samples/videos/sample_dashcam.mp4
"""

import os
import cv2
import numpy as np
from pathlib import Path

SAMPLES_DIR = Path(__file__).parent
IMAGES_DIR = SAMPLES_DIR / "images"
VIDEOS_DIR = SAMPLES_DIR / "videos"
OUTPUT_VIDEO = VIDEOS_DIR / "sample_dashcam.mp4"

# Video settings
FPS = 24
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAMES_PER_IMAGE = 72   # ~3 seconds per image at 24fps
TRANSITION_FRAMES = 24  # 1-second crossfade between images


def load_and_resize(path: Path) -> np.ndarray:
    """Load an image and resize/crop to dashcam frame size."""
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")

    h, w = img.shape[:2]
    target_ratio = FRAME_WIDTH / FRAME_HEIGHT
    src_ratio = w / h

    # Crop to target aspect ratio (center crop)
    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x_start = (w - new_w) // 2
        img = img[:, x_start: x_start + new_w]
    else:
        new_h = int(w / target_ratio)
        y_start = (h - new_h) // 2
        img = img[y_start: y_start + new_h, :]

    return cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_LANCZOS4)


def apply_camera_shake(frame: np.ndarray, intensity: float = 2.0) -> np.ndarray:
    """Apply subtle random translation to simulate dashcam vibration."""
    dx = int(np.random.normal(0, intensity))
    dy = int(np.random.normal(0, intensity))
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (FRAME_WIDTH, FRAME_HEIGHT),
                          borderMode=cv2.BORDER_REFLECT_101)


def apply_slow_zoom(frame: np.ndarray, zoom_factor: float) -> np.ndarray:
    """Apply a slow zoom-in effect to simulate road approach."""
    if abs(zoom_factor - 1.0) < 1e-4:
        return frame
    h, w = frame.shape[:2]
    crop_h = int(h / zoom_factor)
    crop_w = int(w / zoom_factor)
    y1 = (h - crop_h) // 2
    x1 = (w - crop_w) // 2
    cropped = frame[y1:y1 + crop_h, x1:x1 + crop_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


def add_hud_overlay(frame: np.ndarray, frame_idx: int, total_frames: int,
                    image_name: str, speed_kmh: float = 35.0) -> np.ndarray:
    """Add a dashcam HUD overlay: speed, timestamp, filename label."""
    out = frame.copy()
    h, w = out.shape[:2]

    # Semi-transparent bottom bar
    overlay = out.copy()
    cv2.rectangle(overlay, (0, h - 48), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, out, 0.45, 0, out)

    # Speed indicator (simulated)
    speed_jitter = speed_kmh + np.random.normal(0, 0.8)
    speed_text = f"{speed_jitter:.0f} km/h"
    cv2.putText(out, speed_text, (18, h - 16),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 180), 1, cv2.LINE_AA)

    # Scene label
    label = image_name.replace("_", " ").replace(".png", "").title()
    cv2.putText(out, f"[SAMPLE] {label}", (w // 2 - 240, h - 16),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)

    # Fake GPS timestamp
    minutes = frame_idx // (FPS * 60)
    seconds = (frame_idx // FPS) % 60
    ts = f"REC  00:{minutes:02d}:{seconds:02d}"
    ts_size = cv2.getTextSize(ts, cv2.FONT_HERSHEY_DUPLEX, 0.65, 1)[0]
    cv2.putText(out, ts, (w - ts_size[0] - 18, h - 16),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 200, 255), 1, cv2.LINE_AA)

    # Red REC dot
    elapsed = frame_idx / FPS
    if int(elapsed) % 2 == 0:
        cv2.circle(out, (w - ts_size[0] - 50, h - 22), 7, (0, 0, 220), -1)

    return out


def crossfade(img_a: np.ndarray, img_b: np.ndarray, alpha: float) -> np.ndarray:
    """Blend two frames for a smooth transition."""
    return cv2.addWeighted(img_a, 1.0 - alpha, img_b, alpha, 0)


def main():
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(IMAGES_DIR.glob("*.png")) + sorted(IMAGES_DIR.glob("*.jpg"))
    if not image_paths:
        print(f"[ERROR] No images found in {IMAGES_DIR}")
        return

    print(f"Found {len(image_paths)} sample images:")
    for p in image_paths:
        print(f"  - {p.name}")

    frames_loaded = [load_and_resize(p) for p in image_paths]
    print(f"\nGenerating video: {OUTPUT_VIDEO}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(OUTPUT_VIDEO), fourcc, FPS,
                             (FRAME_WIDTH, FRAME_HEIGHT))

    global_frame = 0

    for idx, (frame_base, img_path) in enumerate(zip(frames_loaded, image_paths)):
        next_frame = frames_loaded[(idx + 1) % len(frames_loaded)]
        image_name = img_path.name

        # Zoom range: 1.0 → 1.06 over the image duration
        for f in range(FRAMES_PER_IMAGE):
            zoom = 1.0 + 0.06 * (f / FRAMES_PER_IMAGE)
            zoomed = apply_slow_zoom(frame_base, zoom)
            shaken = apply_camera_shake(zoomed, intensity=1.5)
            out_frame = add_hud_overlay(shaken, global_frame, 0, image_name)
            writer.write(out_frame)
            global_frame += 1

        # Crossfade transition to next image
        for f in range(TRANSITION_FRAMES):
            alpha = f / TRANSITION_FRAMES
            blended = crossfade(frame_base, next_frame, alpha)
            shaken = apply_camera_shake(blended, intensity=1.0)
            out_frame = add_hud_overlay(shaken, global_frame, 0, image_name)
            writer.write(out_frame)
            global_frame += 1

        print(f"  [OK] Processed: {image_name}")

    writer.release()
    total_seconds = global_frame / FPS
    size_mb = OUTPUT_VIDEO.stat().st_size / (1024 * 1024)
    print(f"\n[DONE] Video saved: {OUTPUT_VIDEO}")
    print(f"   Duration : {total_seconds:.1f}s  ({global_frame} frames @ {FPS}fps)")
    print(f"   File size: {size_mb:.1f} MB")
    print(f"   Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")


if __name__ == "__main__":
    main()
