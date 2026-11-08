import os, subprocess
import numpy as np

os.makedirs('/home/daksh/Documents/Projects/floodlock/floodlock_frontend/assets', exist_ok=True)
output_path = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/assets/cinematic_floodlock.mp4'

width, height = 1280, 720
fps = 30
duration_sec = 12
total_frames = fps * duration_sec

cmd = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{width}x{height}',
    '-pix_fmt', 'rgb24',
    '-r', str(fps),
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'veryfast',
    '-crf', '23',
    output_path
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
print(f'Rendering {total_frames} cinematic frames...')

Y, X = np.ogrid[:height, :width]
cx, cy = width / 2.0, height / 2.0

for f in range(total_frames):
    t = f / float(total_frames) # 0.0 to 1.0
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    if t < 0.28:
        # ── CHAPTER 1: STORM SKY & FALLING HERO RAINDROP ──
        sky = (np.linspace(6, 22, height)[:, None] * np.ones((1, width))).astype(np.uint8)
        frame[:, :, 0] = sky
        frame[:, :, 1] = sky + 4
        frame[:, :, 2] = sky + 12

        # Subtle lightning pulse
        if 0.11 < t < 0.14:
            flash = int(55 * np.sin((t - 0.11) / 0.03 * np.pi))
            frame = np.clip(frame.astype(np.int16) + flash, 0, 255).astype(np.uint8)

        # Falling drop coordinate
        prog = t / 0.28
        drop_y = 60 + prog * 490
        drop_x = cx + np.sin(prog * 6) * 15

        dist = np.sqrt((X - drop_x)**2 + (Y - drop_y)**2)
        # Drop aura
        glow = np.clip((40 - dist) * 2.5, 0, 180).astype(np.uint8)
        frame[:, :, 0] = np.clip(frame[:, :, 0] + glow * 0.4, 0, 255).astype(np.uint8)
        frame[:, :, 1] = np.clip(frame[:, :, 1] + glow * 0.8, 0, 255).astype(np.uint8)
        frame[:, :, 2] = np.clip(frame[:, :, 2] + glow, 0, 255).astype(np.uint8)

        # Core droplet
        core_mask = dist < 10
        frame[core_mask] = [240, 250, 255]

    elif t < 0.55:
        # ── CHAPTER 2: WET DADAR TT ASPHALT & RADIAL RIPPLES ──
        prog = (t - 0.28) / 0.27
        frame[:, :, 0] = 5
        frame[:, :, 1] = 7
        frame[:, :, 2] = 10

        impact_y = 560
        dist = np.sqrt(((X - cx) * 0.7)**2 + (Y - impact_y)**2)
        for ring in range(5):
            ring_r = (prog * 450 + ring * 55) % 480
            ring_mask = np.abs(dist - ring_r) < 3.2
            fade = max(0.0, 1.0 - (ring_r / 480.0))
            frame[ring_mask, 0] = np.clip(frame[ring_mask, 0] + int(15 * fade), 0, 255)
            frame[ring_mask, 1] = np.clip(frame[ring_mask, 1] + int(140 * fade), 0, 255)
            frame[ring_mask, 2] = np.clip(frame[ring_mask, 2] + int(210 * fade), 0, 255)

    elif t < 0.80:
        # ── CHAPTER 3: ARABIAN SEA SPRING TIDE & SLUICE LOCK ──
        prog = (t - 0.55) / 0.25
        frame[:, :, 0] = int(12 + prog * 45)
        frame[:, :, 1] = 6
        frame[:, :, 2] = 12

        # Sinusoidal rising sea tide
        wave_y = 480.0 - np.sin(X / 80.0 + f * 0.12) * 28.0 - prog * 90.0
        wave_mask = (Y > wave_y).squeeze()
        frame[wave_mask, 0] = np.clip(frame[wave_mask, 0] + 55, 0, 255)
        frame[wave_mask, 1] = np.clip(frame[wave_mask, 1] + 16, 0, 255)
        frame[wave_mask, 2] = np.clip(frame[wave_mask, 2] + 28, 0, 255)

        # Choke lock boundary box
        choke_alpha = min(1.0, prog * 1.5)
        gate_left, gate_right = int(cx - 220), int(cx + 220)
        gate_top, gate_bot = 240, 420
        frame[gate_top:gate_bot, gate_left:gate_right, 0] = np.clip(frame[gate_top:gate_bot, gate_left:gate_right, 0] + int(90 * choke_alpha), 0, 255)

    else:
        # ── CHAPTER 4: ELEVATED VIADUCT (+8.5m) & NEURAL NETWORK ──
        prog = (t - 0.80) / 0.20
        frame[:, :, 0] = 4
        frame[:, :, 1] = 12
        frame[:, :, 2] = 18

        viaduct_y = 350
        v_mask = (np.abs(Y - viaduct_y) < 4).squeeze()
        frame[v_mask, 0] = 16
        frame[v_mask, 1] = 185
        frame[v_mask, 2] = 129

        v_halo = (np.abs(Y - viaduct_y) < 22).squeeze()
        frame[v_halo, 1] = np.clip(frame[v_halo, 1] + 35, 0, 255)

        for i in range(10):
            nx = int(140 + i * 110)
            ny = int(350 + np.sin(i * 1.4 + f * 0.18) * 65)
            d = np.sqrt((X - nx)**2 + (Y - ny)**2)
            n_mask = (d < 8).squeeze()
            frame[n_mask] = [6, 182, 212]

    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()
print(f'Render Complete! Saved: {output_path} ({os.path.getsize(output_path)} bytes)')
