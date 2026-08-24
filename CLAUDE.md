# LedMerger — Project Context for Claude

## What this project is
A Flask/Docker web app for creating and merging LED rink content for Pixbo Floorball at Wallenstam Arena. It produces stacked MP4 files compatible with the Sedna LED controller.

## Current version: 0.372

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
- Server: NUC at 192.168.0.140, accessed via VS Code Remote SSH (planned move to 192.168.0.150 — see Hosting & migration)
- GitHub: planet4/LedMerger (repo is **public** — never commit secrets)

## File structure
- `app.py` — all backend logic, Flask routes, ffmpeg workers
- `templates/index.html` — entire frontend (single file, ~1800 lines)
- `templates/led_preview.html` — LED preview popup window (60fps, pixel grid, arena view)
- `data/backgrounds/1728/` — 1728px backgrounds (Longside Center)
- `data/backgrounds/1344/` — 1344px backgrounds (Shortside)
- `data/backgrounds/576_variants/` — 576px variant backgrounds
- `data/backgrounds/media_192/` — 192px media backgrounds
- `data/backgrounds/layout.png` — arena photo used in LED preview arena view
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
- Backgrounds: fixed template files — **exact filenames are hardcoded, do not rename**
  - `data/backgrounds/1728/players-template-1728.mp4`
  - `data/backgrounds/1344/players-template-1344.mp4`
  - `data/backgrounds/576_variants/players-template-576.mp4`
  - `data/backgrounds/media_192/players-template-192.mp4`
- Other files in `1728/` and `1344/` are freely renameable — they only appear as dropdown options
- Default timing: 2.1s number, 6s total
- Pop wobble effect: fontsize expression using damped oscillation
  - formula: `base*(1+0.35*exp(-8*t)*cos(12*t))`
- LED Preview button renders real clips at 25fps first, then opens preview
- Export: stacked + all individual files

## LED Preview (led_preview.html)
- 60fps using CSS image-rendering:pixelated (not JS pixel loop)
- GLOW toggle — off by default
- GRID toggle — SVG overlay, off by default
- ARENA VIEW toggle — overlays videos on layout.png arena photo
- SYNC button — resets all videos to t=0
- Arena zone coordinates defined as percentages in ARENA_ZONES array

## Deployment
```bash
sudo docker compose up -d --build
```
Then hard refresh browser (Ctrl+Shift+R).

**Note:** templates are baked into the image (not volume-mounted), and `FLASK_ENV=production` disables Flask template auto-reload — so **all** changes, including `index.html` / `led_preview.html`, require `docker compose up -d --build` to go live. A plain file copy is not enough.

## Authentication
- Server-side session auth (added v0.365). A `before_request` guard rejects every route except `/` and `/api/login` with 401 unless logged in — so the API cannot be used without a session, not just the UI.
- `/api/login` checks the password (case-insensitive, trimmed) and sets a 90-day session cookie. Rename/delete/save all rely on the session; only file **delete** still shows a confirm dialog.
- Password comes from `APP_PASSWORD` (env var). Current value lives in `.env` (gitignored) — **currently `Floorball!`**. Not in the repo (repo is public).
- Session secret: `SECRET_KEY` env var if set, else a generated key persisted at `/app/library/.secret_key` (i.e. `data/library/.secret_key`). Keep this file on migration or all sessions invalidate (users just re-login).

## Environment variables (docker-compose.yml + .env)
- `FLASK_ENV=production`
- `TEAMSCRAPER_BASE` — default `http://192.168.0.140:5020`; used by the Players "Pick team" feature.
- `APP_PASSWORD` — from `.env` (gitignored). `.env.example` documents the format.

## External dependencies
- **Teamscraper** at `192.168.0.140:5020` (the `/home/planet4/docker/teamscraper` project, container `sporteventtv-sporteventtv-1`, also serves `teamscraper.planet4.nu`). Players "Pick team" proxies `/roster-scheduler/files` (team list) and `/roster/<id>.json` (roster) through it. If teamscraper is down, Pick team breaks; nothing else does. (Not the `teamscraper-test` container on :5029 — that's dummy data.)
- **Public URL** `ledmerger.planet4.nu`: Cloudflare (proxied) → swag reverse proxy (nginx) → the container's port 5000. swag config lives on the host at `/srv/docker/swag/config` (NOT in this repo); its fail2ban `ignoreip` now includes Cloudflare's IPv4 ranges. See memory `infra-cloudflare-swag` for the outage lessons (banned Cloudflare edge IPs → whole-site 520/521; jail.local is copied to `/etc/` on container start).

## Hosting & migration (planned move 192.168.0.140 → 192.168.0.150)
To move the container, copy/recreate on the new host:
1. The repo (git clone) — code, compose, Dockerfile.
2. `.env` (NOT in git) — recreate with `APP_PASSWORD=…`.
3. `data/` volumes — **`data/library` (162M) is the irreplaceable content**; also `data/backgrounds`, `data/fonts`, and `data/library/.secret_key`. `data/outputs` + `data/uploads` are ephemeral (safe to skip).
4. Update references to the old IP `192.168.0.140`:
   - `TEAMSCRAPER_BASE` in `docker-compose.yml`/`.env` (teamscraper stays on .140, so the LAN IP is still valid — only change if teamscraper also moves).
   - **swag reverse-proxy** on the host: the ledmerger site conf `proxy_pass` must point at the new host:5000. swag config is NOT in this repo — it lives at `/srv/docker/swag/config` (copied to `/etc/…` at container start).
5. `docker compose up -d --build`, then verify: login with the password, Library loads, Players "Pick team" reaches teamscraper, and the public URL returns 200 (watch swag fail2ban — see memory).

## Cleanup outputs
```bash
rm -f data/outputs/*.mp4
rm -f data/uploads/*
```
Stale files to clean when convenient: `data/library/Auto Generated/` holds two April test renders from the removed scheduler (root-owned; `sudo rm`).

## Important rules
- Never change build_stacked_export() without verifying on physical displays
- Longside Left and Right always use same source to avoid visible cuts on displays
- All three tabs must call the same build_stacked_export() function
- The 576 display appears 3 times in the strip — left, right, and row 5 tail
- FONT_PATH = /app/fonts/Road_Rage.otf (correct filename — do not change)
- **After every change, update CHANGELOG.md** — add a summarized entry under the current version (or bump the version if it's a meaningful release). Keep it brief: what changed and why, not line-by-line details.
- **Version scheme:** `0.1` = initial, `0.11` / `0.12` = incremental updates to 0.1, `0.2` = next major change, `0.21` / `0.22` = incremental updates to 0.2, etc. Bump to the next major (e.g. `0.3`) only for significant rewrites or feature additions. Increment the sub-version (e.g. `0.21` → `0.22`) for smaller fixes and features.
- **After bumping the version**, update both `CLAUDE.md` ("Current version") and the subtitle line in `templates/index.html` (format: `Pixbo LED Rink Content Creator v0.XX`).
- **When implementing something from ROADMAP.md**, remove it from the roadmap after it's done.