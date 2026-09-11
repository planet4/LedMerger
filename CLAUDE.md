# LedMerger — Project Context for Claude

## What this project is
A Flask/Docker web app for creating and merging LED rink content for Pixbo Floorball at Wallenstam Arena. It produces stacked MP4 files compatible with the Sedna LED controller.

## Current version: 0.405

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
- Server: NUC2 at 192.168.0.150, accessed via VS Code Remote SSH (migrated from 192.168.0.140 — see Hosting & migration)
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
- `data/library/<category>/` — one folder per category (built-in + user-added); `data/library/categories.json` persists user-added category names; `data/library/metadata.json` holds per-file descriptions + cached ffprobe duration; `data/library/<category>/.led_preview/` holds LED Preview sidecars (see Library tab section)

## Three content tabs + Library
1. **File Merger** — Upload 5 files, merge into stacked export. All 5 upload boxes (and every tile-mode sub-slot) share **one persistent `<input type="file">`** (`#sharedUploadInput`, dynamically retargeted before each open) instead of one per slot — browsers remember the last folder used *per input element*, so multiple inputs meant the file picker kept jumping between different remembered folders. Don't revert to per-slot inputs.
2. **Players** — Fixed Pixbo template, Road Rage font, pop-wobble animation, number fades to name
3. **Custom** — Per-display text with configurable backgrounds and timing
4. **Library** — see below

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
- **Batch mode** (multi-player): combined-batch output is named from the team (`batch_<team>_<jobid>.mp4`) — "Pick team" sends `team_name` explicitly in the request (preferred), falling back to scanning `players[0]` for the `{number:'PIXBO', name:<team>}` sentinel row convention (also used by CSV import) for older callers, then to the first couple of player names. Batch mode does **not** render individual per-display clips (unlike single-generate/Custom), so batch-saved library files always hit LED Preview's extraction fallback rather than getting instant sidecars — see ROADMAP.

## Library tab
- **Categories**: 12 built-in (`_DEFAULT_LIBRARY_CATEGORIES` in app.py) + any user-added ones persisted in `data/library/categories.json`. Every category `<select>` (`class="cat-select"`) has a "+ New category…" option that prompts, POSTs `/api/library/categories/add`, creates the folder, and live-refreshes every dropdown on the page — except the Library tab's own collapsible section card for a brand-new category, which only appears after a reload (server-rendered from `library_categories` at page-load time).
- **Sort order**: category cards re-sort by file count (most-populated first, ties keep original order) after every `loadLibrary()` — moves existing DOM nodes via `appendChild`, doesn't rebuild them, so expanded/collapsed state survives.
- **Duration cache**: `/api/library` used to `ffprobe` every file on every request (several seconds with a non-trivial library). Now cached in `data/library/metadata.json` (same store as descriptions) keyed by file mtime — only re-probed when new/replaced.
- **Download All**: folder-zip icon per category header → `/api/library/download-all/<category>` streams a ZIP (uncompressed/STORED — the mp4s are already h264).
- **LED Preview sidecars**: `data/library/<cat>/.led_preview/<filename-stem>/d0..d4.mp4` — the 5 per-display clips LED Preview needs. Saved directly at Save-to-Library time when the source tab already rendered them individually (Players single-generate, Custom, File Merger's raw uploads); otherwise built lazily on first preview click by cropping the exact regions `build_stacked_export()` wrote them into (`extract_led_preview_clips()` — inverse of that layout, keep in sync if it ever changes) and cached for next time. **Only attempted on an actual 1600×1200 source** — probed via ffprobe first; anything else (e.g. "Non Stacked" category, which holds raw single-display clips) skips straight to Merged-File-only, since those crop offsets are meaningless for a non-stacked source. Rename / category-change / delete all move or remove the sidecar dir alongside the file — don't let that drift (an orphaned/stale sidecar is exactly what caused a real bug: silently-wrong cropped output reused under a filename that no longer matched).

## LED Preview (led_preview.html)
- Three mutually-exclusive view modes as big buttons (styled like the main app's buttons — `#1E1E26`/`#2E2E3A`/`#888` idle, red active), default **ARENA VIEW**:
  - **ARENA VIEW** — overlays the 5 per-display videos on layout.png (arena photo), positioned via `ARENA_ZONES` percentage coordinates
  - **MERGED FILE** — plays the single final stacked file directly (`<video controls>`); only enabled when the opener passes a `merged=` path (currently: Library's LED Preview button, since the library file itself *is* the merged export). Disabled/grayed otherwise.
  - **SEPARATE FILES** — the original per-display row/grid view, 60fps via CSS `image-rendering:pixelated` (not a JS pixel loop)
- Secondary "OPTIONS" row below the mode buttons: GRID, GLOW, LIGHTS OFF, SYNC, SPEED (1×→1.5×→2×→3×→4×→0.5×), ± ZOOM, FULLSCREEN. GRID/GLOW and LIGHTS OFF are each specific to one mode (Separate Files, and Arena View respectively — no equivalent in the other); ZOOM applies to Arena View + Separate Files (separate scale state per mode — Arena's canvas fills the window differently than Separate Files' auto-fit stage); SYNC (resets all clips to t=0 — they loop independently and can drift) applies to Arena+Separate but not Merged File. Auto-disabled (grayed, non-interactive incl. keyboard shortcuts) when not applicable to the current mode.
- **LIGHTS OFF** (Arena View only): dims just the arena photo layer (a semi-transparent black `fillRect` drawn after the photo but before the LED zones each frame in `drawArenaView()`) — the LED video content is drawn on top afterward, so it stays at full brightness, simulating house lights down / boards still lit.
- If the opener passes no per-display `d0..d4` params at all (e.g. a "Non Stacked" library file — see below), ARENA VIEW/SEPARATE FILES are disabled and the window opens straight to MERGED FILE.
- Popup window opens sized to `window.screen.availWidth/Height` (maximized, not the browser Fullscreen API — tried that, wasn't what was wanted) via the shared `openLedPreviewWindow()` helper in index.html — all 4 places that open this window go through it.

## Deployment
```bash
sudo docker compose up -d --build
```
Then hard refresh browser (Ctrl+Shift+R).

**Note:** templates are baked into the image (not volume-mounted), and `FLASK_ENV=production` disables Flask template auto-reload — so **all** changes, including `index.html` / `led_preview.html`, require `docker compose up -d --build` to go live. A plain file copy is not enough.

## Authentication
- Server-side session auth (added v0.365). A `before_request` guard rejects every route except `/` and `/api/login` with 401 unless logged in — so the API cannot be used without a session, not just the UI.
- `/api/login` checks the password (case-insensitive, trimmed) and sets a 90-day session cookie. Rename/delete/save all rely on the session; only file **delete** still shows a confirm dialog.
- Password comes from `APP_PASSWORD` (env var). The current value lives only in `.env` (gitignored) — **never write the literal password in this file or any other tracked file; this repo is public.** To read it: `grep APP_PASSWORD .env` on the server.
- Session secret: `SECRET_KEY` env var if set, else a generated key persisted at `/app/library/.secret_key` (i.e. `data/library/.secret_key`). Keep this file on migration or all sessions invalidate (users just re-login).

## Environment variables (docker-compose.yml + .env)
- `FLASK_ENV=production`
- `TEAMSCRAPER_BASE` — `http://192.168.0.150:5020` (moved here from .140 — see External dependencies); used by the Players "Pick team" feature.
- `APP_PASSWORD` — from `.env` (gitignored). `.env.example` documents the format.

## External dependencies
- **Teamscraper** at `192.168.0.150:5020` — moved from .140 to .150 (same host as ledmerger now) at some point after the initial ledmerger migration; `.140:5020` no longer answers. `docker-compose.yml`'s `TEAMSCRAPER_BASE` was updated to match and confirmed live (container env var verified, `.150:5020` responds). The `/home/planet4/docker/teamscraper` project, container `sporteventtv-sporteventtv-1`, also serves `teamscraper.planet4.nu` — if that public hostname still resolves through swag on .140, its proxy target likely needs repointing to .150 too (not verified here; swag config isn't in this repo). Players "Pick team" proxies `/roster-scheduler/files` (team list) and `/roster/<id>.json` (roster) through it. If teamscraper is down, Pick team breaks; nothing else does. (Not the `teamscraper-test` container on :5029 — that's dummy data.)
- **Public URL** `ledmerger.planet4.nu`: Cloudflare (proxied) → swag reverse proxy (nginx, **still runs on 192.168.0.140**, not migrated) → ledmerger container's port 5000 on **192.168.0.150**. swag config lives on the host (.140) at `/srv/docker/swag/config` (NOT in this repo); its fail2ban `ignoreip` now includes Cloudflare's IPv4 ranges. See memory `infra-cloudflare-swag` for the outage lessons (banned Cloudflare edge IPs → whole-site 520/521; jail.local is copied to `/etc/` on container start).

## Hosting & migration (done: moved 192.168.0.140 → 192.168.0.150, host `nuc2`)
LedMerger itself now runs on **192.168.0.150** (`nuc2`). Note what did *not* move:
- **teamscraper** has since also moved to .150 (`TEAMSCRAPER_BASE` in `docker-compose.yml` updated to `http://192.168.0.150:5020` and confirmed live). It stayed on .140 at the time of the ledmerger move itself — this happened separately, later.
- **swag** reverse proxy stays on .140 too — its ledmerger site conf `proxy_pass` was repointed to `192.168.0.150:5000` and this is confirmed working (public URL returns 200). swag config is NOT in this repo — lives at `/srv/docker/swag/config` on .140.

What was carried over during the move: repo (git clone), `.env` (not in git, recreated with `APP_PASSWORD=…`), and the `data/` volumes — `data/library` (162M, irreplaceable), `data/backgrounds`, `data/fonts`, and `data/library/.secret_key` (keeping this file preserved existing login sessions). `data/outputs`/`data/uploads` are ephemeral and were not carried over.

If another host migration happens in the future, repeat this process and update this section's IPs again.

## Cleanup outputs
**This happens automatically** — `_daily_cleanup()` (app.py, started as a module-level `threading.Thread` at import) deletes *everything* in `data/uploads/` and `data/outputs/` at midnight each night. Anything generated but not saved to the Library is gone by the next day. That's also why a session running past midnight can see files disappear mid-use (see ROADMAP "Output file TTL").

To clear them manually mid-session:
```bash
rm -f data/outputs/*.mp4
rm -f data/uploads/*
```
Safe at any time — library saves are full `shutil.copy2()` copies, so nothing in `data/library/` depends on these folders.

Stale files to clean when convenient: `data/library/Auto Generated/` holds two April test renders from the removed scheduler (root-owned; `sudo rm`).

## Security posture (audited 2026-09-11)
- **`debug` is `False`** in `app.run()` and must stay that way. Two reasons: the Werkzeug interactive debugger would expose source + locals + a Python console on any unhandled exception; and `use_reloader` follows `debug`, which would run the module twice and start a second `_daily_cleanup` thread. Verify with `docker logs sedna-merger | grep -iE "Debug mode|Debugger is active"` — want `Debug mode: off` and no `Debugger is active!`.
- The `WARNING: This is a development server` line in the logs is Werkzeug noting it's the dev *server*. Unrelated to the debug flag, prints regardless, and is a known accepted gap — not a vulnerability.
- **Never bind to `127.0.0.1`.** Traffic arrives from the swag proxy on a *different host* (`192.168.0.140`, ~all requests in the access log), so localhost-binding breaks the public site without reducing exposure.
- **If gunicorn is ever introduced, it must be `--workers 1`** (threads are fine). `jobs = {}` (app.py) is an in-memory dict holding all job progress, read by `/api/status/<job_id>`; multiple workers means the polling request hits a process that doesn't have that job → `404 Unknown job` on every progress bar, while the render silently succeeds elsewhere. `_daily_cleanup` would also run once per worker.
- Known, accepted gaps: container runs as **root**; no `cap_drop`/`no-new-privileges`/`read_only` in compose; port published on `0.0.0.0:5000`, so LAN clients can reach the app directly, bypassing Cloudflare and swag's fail2ban (session auth still applies).
- `.env` is not tracked — keep it that way, and **never put the password value in any tracked file** (it leaked into `CLAUDE.md` once and is still in git history at `4bce7c5`).

## Important rules
- Never change build_stacked_export() without verifying on physical displays
- Longside Left and Right always use same source to avoid visible cuts on displays
- All three tabs must call the same build_stacked_export() function
- The 576 display appears 3 times in the strip — left, right, and row 5 tail
- FONT_PATH = /app/fonts/Road_Rage.otf (correct filename — do not change)
- **After every change, update CHANGELOG.md** — add a summarized entry under the current version (or bump the version if it's a meaningful release). Keep it brief: what changed and why, not line-by-line details.
- **Version scheme:** `0.1` = initial, `0.11` / `0.12` = incremental updates to 0.1, `0.2` = next major change, `0.21` / `0.22` = incremental updates to 0.2, etc. Bump to the next major (e.g. `0.3`) only for significant rewrites or feature additions. Increment the sub-version (e.g. `0.21` → `0.22`) for smaller fixes and features.
- **After bumping the version**, update all three places — `CLAUDE.md` ("Current version"), the subtitle line in `templates/index.html`, and the `README.md` title heading (both use the format `Pixbo LED Rink Content Creator v0.XX`). README is the public repo's front page, so a stale version there is the most visible one. Verify with: `grep -rn "Content Creator v0" README.md templates/index.html; grep "Current version" CLAUDE.md`
- **When implementing something from ROADMAP.md**, remove it from the roadmap after it's done.