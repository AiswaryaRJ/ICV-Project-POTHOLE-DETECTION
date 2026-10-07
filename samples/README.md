# Sample Media Assets

This directory contains built-in demo media for the **RoadPulse** pothole detection app.
No model weights or real footage required — use these to instantly demo the system.

## 📁 Directory Structure

```
samples/
├── images/
│   ├── pothole_daytime_large.png        # Large daytime pothole (High severity)
│   ├── pothole_multiple_cracks.png      # Multiple cracks, overcast (High severity)
│   ├── pothole_nighttime_rain.png       # Rain-filled pothole, night (Medium severity)
│   ├── pothole_highway_damage.png       # Highway road surface damage (Medium severity)
│   └── pothole_intersection_severe.png  # Severe intersection damage (High severity)
│
├── videos/
│   └── sample_dashcam.mp4              # 20s HD dashcam simulation video (1280x720 @ 24fps)
│
└── generate_sample_video.py            # Script to regenerate the sample video
```

## 🎬 Regenerating the Sample Video

If you want to recreate `sample_dashcam.mp4` from the images (e.g., after adding new sample images):

```bash
python samples/generate_sample_video.py
```

The script adds:
- Slow dashcam zoom effect
- Subtle camera shake simulation  
- HUD overlay (speed, timestamp, REC indicator)
- Smooth crossfade transitions between scenes

## ➕ Adding Your Own Samples

1. Place your `.png` or `.jpg` images in `samples/images/`
2. Add an entry in `app/app.py` under `SAMPLE_IMAGE_META` dict
3. Re-run `generate_sample_video.py` to include them in the video
