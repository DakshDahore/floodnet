#!/usr/bin/env python3
import os
import subprocess

assets_dir = "/home/daksh/Documents/Projects/floodlock/floodlock_frontend/assets"
img1 = os.path.join(assets_dir, "scene1_macro_drop.jpg")
img2 = os.path.join(assets_dir, "scene2_flooded_street.jpg")
img3 = os.path.join(assets_dir, "scene3_sluice_lock.jpg")
img4 = os.path.join(assets_dir, "scene4_drone_skyline.jpg")
out_mp4 = os.path.join(assets_dir, "flood_genesis.mp4")

# Pre-scale each image to 1280x720 30fps clip of 4.5s
# Then xfade them: 4.5 + 3.5 + 3.5 + 3.5 = 15.0s
cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-t", "4.5", "-framerate", "30", "-i", img1,
    "-loop", "1", "-t", "4.5", "-framerate", "30", "-i", img2,
    "-loop", "1", "-t", "4.5", "-framerate", "30", "-i", img3,
    "-loop", "1", "-t", "4.5", "-framerate", "30", "-i", img4,
    "-filter_complex",
    (
        "[0:v]scale=1280:720,setsar=1[v0];"
        "[1:v]scale=1280:720,setsar=1[v1];"
        "[2:v]scale=1280:720,setsar=1[v2];"
        "[3:v]scale=1280:720,setsar=1[v3];"
        "[v0][v1]xfade=transition=fade:duration=1.0:offset=3.5[x1];"
        "[x1][v2]xfade=transition=fade:duration=1.0:offset=7.0[x2];"
        "[x2][v3]xfade=transition=fade:duration=1.0:offset=10.5[outv]"
    ),
    "-map", "[outv]",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "ultrafast",
    "-crf", "20",
    "-g", "5",
    "-movflags", "+faststart",
    out_mp4
]

print("Compiling flood_genesis.mp4...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    size = os.path.getsize(out_mp4)
    print(f"SUCCESS: {out_mp4} created ({size} bytes)")
else:
    print(f"FAILED: {res.stderr[:500]}")
