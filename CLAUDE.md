# LedMerger — Project Context for Claude

## What this project is
A Flask/Docker web app for creating and merging LED rink content for Pixbo Floorball at Wallenstam Arena. It produces stacked MP4 files compatible with the Sedna LED controller.

## Critical — Export format
The stacked export MUST always be exactly 1600×1200px, 50fps, h264/yuv420p.
The layout matches the After Effects/ledventure.org reference template:
- Row 1 (y=0):   Shortside 1344px full
- Row 2 (y=64):  Shortside last 384px + LongsideLeft 576px at x=384
- Row 3 (y=128): LongsideCenter first 1600px of 1728
- Row 4 (y=192): LongsideCenter last 768px + LongsideRight 576px at x=768
- Row 5 (y=256): LongsideLeft last 384px + Media 192px at x=384
- Rows 6-19: black padding to 1200px

This layout is handled by `build_stacked_export()` in app.py — never change this function without verifying against the physical LED displays.

## Display sizes (fixed)
- Shortside: 1344×64px
- Longside Left: 576×64px
- Longside Center: 1728×64px
- Longside Right: 576×64px
- Media: 192×64px

## Tech stack
- Backend: Flask (app.py)
- Video processing: ffmpeg (filter_complex)
- Frontend: Tailwind CSS, vanilla JS, Canvas API
- Deployment: Docker Compose

## File structure
- `app.py` — all backend logic, Flask routes, ffmpeg workers
- `templates/index.html` — entire frontend (single file, ~1800 lines)
- `templates/led_preview.html` — LED preview popup window
- `data/backgrounds/` — background video library
- `data/backgrounds/576_variants/` — 576px variant backgrounds
- `data/backgrounds/media_192/` — 192px media backgrounds
- `data/fonts/` — font files (.ttf, .otf)
- `data/uploads/` — temporary upload storage (safe to delete)
- `data/outputs/` — generated video files (safe to delete)

## Three tabs
1. **File Merger** — Upload 5 files, merge into stacked export
2. **Players** — Fixed Pixbo template, Road Rage font, pop-wobble animation, number fades to name
3. **Custom** — Per-display text with configurable backgrounds and timing

## Players tab specifics
- Font: Road Rage (Road_Rage.otf) — always, not configurable
- Color: white — always
- Backgrounds: fixed template files must exist in data/backgrounds/
  - players-template-1728.mp4
  - players-template-1344.mp4
  - 576_variants/players-template-576.mp4
  - media_192/players-template-192.mp4
- Default timing: 2.1s number, 6s total
- Pop wobble effect: fontsize expression using damped oscillation

## Deployment
```bash
sudo docker compose up -d --build
```
Then hard refresh browser (Ctrl+Shift+R).

## Important rules
- Never change build_stacked_export() without verifying on physical displays
- Longside Left and Right should use same source to avoid visible cuts on displays
- All three tabs must call the same build_stacked_export() function
- The 576 display appears 3 times in the strip — left, right, and row 5 tail
