# Changelog

All notable changes to the Pixbo LED Merger project are documented here.

Version scheme: `0.1` = initial, `0.11` / `0.12` = incremental updates, `0.2` = major change.

## Security & docs — 2026-09-11 (no code changes)

- Audited against a `debug=True` vulnerability found in the sibling SportEventTV app — ledmerger was never affected (`debug=False`, confirmed in the container log).
- Removed the literal `APP_PASSWORD` from `CLAUDE.md` and moved all host/topology/security detail to a gitignored `CLAUDE.local.md`; this repo is public. Already-pushed history still contains the password, so it's being rotated separately.
- `TEAMSCRAPER_BASE` moved from a hardcoded host to `.env`.
- Fixed a wrong claim in README/ROADMAP: `_daily_cleanup()` does wipe `data/uploads` and `data/outputs` nightly.

---

## [0.405] - 2026-09-02

### LED Preview — LIGHTS OFF for Arena View

- New OPTIONS toggle (Arena View only): dims just the arena photo, leaving the LED display content drawn on top at full brightness — simulates the arena's house lights going down while the boards keep glowing, without touching the actual video content.

---

## [0.404] - 2026-08-26

### LED Preview — zoom now works in Arena View too

- ZOOM was gated to Separate Files only. Enabled it for Arena View as well (separate scale state, since Arena's canvas fills the whole window differently than Separate Files' auto-fit stage) — GRID/GLOW stay Separate-Files-only since they're per-panel overlays with no Arena equivalent.

---

## [0.403] - 2026-08-26

### Fixed confusing "already in use" when renaming a merge output

- `data/outputs/` is a session-scoped working folder the user has no visibility into (separate from the library). Renaming a fresh merge result could collide with a same-named leftover from an earlier attempt in the same session, producing a confusing "Name already in use" for a name that clearly wasn't in the library. Now auto-dedupes with a " (1)", " (2)"… suffix instead of blocking, matching how Save-to-Library already handles the same situation.

---

## [0.402] - 2026-08-26

### File Merger — one shared file picker instead of one per slot

- Each of the 5 display slots (and every tile sub-slot) had its own separate `<input type="file">`. Browsers remember the last folder used *per input element*, so switching slots kept jumping to whatever folder that specific slot's input last remembered, instead of wherever you'd just been browsing.
- Consolidated to a single persistent, dynamically-retargeted `<input type="file">` for the whole tab. Drag-and-drop is untouched (it never used the input). Can't verify actual Windows file-dialog memory behavior from this environment — this is the standard fix for that class of issue, please confirm it actually helps.

---

## [0.401] - 2026-08-26

### Fixed: Save to Library failing with "File not found" after renaming an output

- `renameOutputFile()` located the Save-to-Library button by hopping exactly 2 siblings from the Rename button — with the row's actual element order that lands on the trailing status `<span>`, not the Save button, so its `onclick` never got updated to the new filename. Clicking Save then POSTed the stale, now-renamed-away filename, which the backend correctly rejects as not found. Now looks the button up within its row instead of counting siblings.

---

## [0.40] - 2026-08-26

### LED Preview — no more crash on "Non Stacked" (raw single-display) files

- "Non Stacked" category files are raw single-display clips, not 1600×1200 stacked exports — `build_stacked_export()`'s crop offsets don't apply to them, so LED Preview's extraction fallback was failing with an ffmpeg "Invalid argument" error and blocking the preview entirely.
- Now probes the source's actual dimensions first; anything that isn't 1600×1200 skips extraction and opens straight to the Merged File view instead (Arena View / Separate Files get disabled/grayed for that file, since there's nothing to split).
- While tracking this down, found the actual root cause of the bad data: rename/category-move/delete never cleaned up a file's LED-preview sidecar folder, so it could go orphaned (still on disk, unreachable, wasted space) or — worse — get silently reused under a filename that no longer matches its content. Rename and category-change now move the sidecar along with the file; delete removes it.

---

## [0.399] - 2026-08-26

### Library — categories sorted by file count

- Category cards now sort most-populated first after every load, instead of the fixed curated order burying whichever categories people actually use. Empty categories sink to the bottom, ties keep the original order. Just reorders the existing card elements — no rebuild, so nothing loses its expanded/collapsed state.

---

## [0.398] - 2026-08-26

### LED Preview — bigger window by default, more speed steps

- Speed cycle extended: 1× → 1.5× → 2× → 3× → 4× → 0.5× (was capped at 2×).
- LED Preview popup now opens sized to the screen's available area (`window.screen.availWidth/Height`, positioned at 0,0) instead of a fixed 1280×600 — i.e. maximized, not the browser Fullscreen API (tried that first; turned out not to be what was wanted — reverted). All 4 places that open the window now go through one shared `openLedPreviewWindow()` helper instead of duplicating the popup-size string.

---

## [0.397] - 2026-08-26

### Library — custom categories

- Every category dropdown (Library tab, and every "Save to Library" picker on File Merger/Players/Custom) now has a "+ New category…" option at the bottom. Picking it prompts for a name, creates it server-side (new folder under `data/library/`), and refreshes every category dropdown on the page immediately — no reload needed to *use* the new category.
- New categories persist in `data/library/categories.json` (on top of the 12 built-in ones), survive redeploys, and get their own collapsible section in the Library tab on next page load.
- Consolidated 3 separately-hardcoded copies of the category list (Jinja section loop, output-row Save selects, Library tab's own selects) down to one server-side list passed into the template, eliminating a source of drift.

---

## [0.396] - 2026-08-26

### Library — Download All (zip) per category

- New folder-zip icon in each category header, next to Upload — downloads every file in that category as one `.zip` (uncompressed/STORED, since the mp4s are already h264 — re-compressing would just burn CPU for no size gain). Useful for e.g. grabbing all "SSL Players Men" clips at once instead of one-by-one.

---

## [0.395] - 2026-08-26

### Fixed batch filename actually using the team name

- v0.393's team-name-in-filename fix relied on inferring the team name from a `{number:'PIXBO', name:<team>}` sentinel row in the players list — which turned out not to reliably carry through, so combined batches were falling back to player names instead. Now "Pick team" sends the team name explicitly (`team_name` in the request), and the backend prefers that; the sentinel-row scan and player-name fallback are still there for CSV import / older callers.
- Editing row 1 (the team-name slide, number `PIXBO`) in the batch list now also updates what the filename uses.

---

## [0.394] - 2026-08-26

### Two usability fixes

- **Library tab was slow to open** (several seconds) — `/api/library` ran `ffprobe` on every single file on every load to get its duration. Now cached (keyed by file mtime) in the same meta store as descriptions, so only new/replaced files get probed; repeat loads are just filesystem stats.
- **Reloading always landed back on File Merger** — the active tab wasn't persisted anywhere. Now saved to `localStorage` on every tab switch and restored on load, so a reload keeps you where you were (Players, Custom, Library).

---

## [0.393] - 2026-08-26

### Players batch — named output files instead of bare job ids

- Combined-batch exports were always named `batch_lineup_<jobid>.mp4`. Now named after the team/roster: `batch_<team-name>_<jobid>.mp4` when picked via "Pick team" (or CSV import, same convention), else from the first couple of player names, keeping a short id suffix to avoid collisions.

---

## [0.392] - 2026-08-26

### LED Preview window — matched to the main app's look

- Switched from the terminal/monospace Courier New look to the main app's Outfit font and exact button styling (same colors/radius as GENERATE PLAYER / LED PREVIEW): mode buttons and options buttons now use `#1E1E26` bg / `#2E2E3A` border / `#888` text at rest, red on hover/active — instead of the low-contrast near-black-on-black that was hard to read.
- Options row background lightened to match, so it reads clearly as a secondary strip rather than disappearing into the header.

---

## [0.391] - 2026-08-26

### Library — dropped the redundant plain Preview button

- Now that LED Preview has a MERGED FILE mode that plays the library file directly (same as the old plain Preview button did), having both was confusing. Removed the plain ▶ Preview button/modal from the Library tab's file rows — the remaining ▶ button opens LED Preview (Arena / Merged File / Separate Files). The modal itself (`libPreviewModal`) stays, since `previewOutputFile()` still uses it for the not-yet-saved output-file lists on File Merger/Players/Custom.

---

## [0.39] - 2026-08-26

### LED Preview window — redesigned header

- Replaced the small ARENA VIEW toggle with 3 big mode buttons (matching the main app's button styling): **ARENA VIEW** (default), **MERGED FILE**, **SEPARATE FILES** — mutually exclusive views instead of an overlay toggle.
- New **MERGED FILE** mode plays the actual final stacked `.mp4` directly in a plain `<video controls>` player — the exact file that ships, as ground truth. Only available when the opener supplies a `merged=` path (currently: Library's LED Preview button, since the library file itself *is* the merged export); disabled/grayed otherwise.
- GRID, GLOW, SYNC, +/−ZOOM moved into a smaller secondary options row, and disabled (grayed, non-interactive — including via keyboard shortcuts) when not applicable to the current mode: GRID/GLOW/ZOOM only apply to Separate Files, SYNC applies to Arena + Separate but not Merged File.
- New **SPEED** button cycling playback rate (1× → 1.5× → 2× → 0.5×) across all clips, including the merged video.
- Removed the SCALE/FPS readouts (dev-y and not useful for actual use).

---

## [0.38] - 2026-08-26

### Library — LED Preview for saved files

- New **LED Preview** button (grid icon) next to each library file's normal Preview button. Opens the same multi-display `led_preview.html` simulator used by the other tabs, without touching the existing Preview button/modal (still plays the merged file as-is — that's the one that actually gets used).
- **Save to Library** on File Merger, Players (single-generate), and Custom now also tucks away the 5 individual per-display source clips as hidden sidecars (`data/library/<cat>/.led_preview/<stem>/d0..d4.mp4`) alongside the merged file, so LED Preview opens instantly — no processing at click time.
- Library files saved before this existed (or via Players batch, which doesn't render individual clips) fall back to on-demand extraction: crops the 5 display regions back out of the stacked 1600×1200 file (exact inverse of `build_stacked_export()`'s layout — read, never modified) and caches the result into the same sidecar location, so every preview after the first is instant too.
- Removed the now-implemented "Arena view for library files" item from `ROADMAP.md`.

---

## Documentation — 2026-08-24 (no code changes)

- Documented server-side auth, `APP_PASSWORD`/`.env`, the `data/library/.secret_key` session secret, and all env vars in `CLAUDE.md` and `README.md`.
- Added a **Hosting & migration checklist** to `CLAUDE.md` ahead of moving the container to a new host: what to copy (`data/library` is the irreplaceable content), the `.env`/secret-key to recreate, the teamscraper dependency, and the reverse-proxy repoint (proxy config lives outside this repo).
- Noted that templates are baked into the image (production disables auto-reload) so every change needs `--build`.
- Recorded discussed-but-unbuilt ideas in `ROADMAP.md`: arena/LED preview for library files, and saving the arena preview.

---

## [0.372] - 2026-07-05

### Players tab — accented-name vertical alignment
- Names with accents (É, Å, Ä, Ö…) previously sat lower than plain names: the text was vertically centered by per-string ink height, which grows when an accent adds height above the caps. Now anchored by the font's global ascent/descent (accent-independent), so every name shares the same baseline.
- Name fill reduced ~90%→~78% of the strip height to reserve headroom so accents don't clip at the top. Names render slightly smaller.
- Players tab only; the Custom worker's positioning is unchanged.

---

## [0.371] - 2026-07-05

### Players tab — Road Rage zero
- The Road Rage font's `0` glyph is broken; the app now auto-substitutes `0`→`O` in player numbers at render time (and in the preview canvas), so it displays correctly without typing `O` by hand. Display-only — output filenames and stored numbers keep the real digit.

---

## [0.37] - 2026-07-05

### Players tab — batch
- Added a **"Save all to [category]"** bar in the batch results header — saves every generated player to one chosen category in a single click (sequential, with per-row status ticks and a running count), instead of saving each of 24 rows individually. Individual save buttons remain for one-offs.

---

## [0.369] - 2026-07-05

### Library
- Deleting a library file no longer asks for the password — the login session already covers it; replaced with a simple confirm dialog (delete is permanent)

---

## [0.368] - 2026-07-05

### Players tab — Pick team
- "Pick team" now lists the stored **roster** files (`/roster-scheduler/files`) instead of the schedule feed (`/scheduler/files`) — the dropdown shows the actual up-to-date rosters kept in teamscraper (Pixbo IBF DJ/DV/Damakademi/F11/…), so a new season's rosters appear automatically
- Rosters with no jersey number (`number: null`) now import with a blank number (skips the number phase) instead of the literal text "null"

---

## [0.367] - 2026-07-05

### Fixed — public site outage (Cloudflare 520/521)
- The auth added in 0.365 made logged-out page loads fire six 401 API calls, which the reverse proxy's fail2ban read as an attack — it banned the CDN's edge IPs, taking the public site down while LAN access kept working
- Frontend now skips all data loading until logged in (page reloads with a session after login), so logged-out visits produce zero 401s
- Infra (outside repo): unbanned those IPs and added the CDN's published IPv4 ranges to fail2ban's `ignoreip`, so edge IPs can never be banned again

---

## [0.366] - 2026-07-05

### Auth
- Password changed (set via `APP_PASSWORD` in docker-compose)
- Removed the extra password prompt when renaming library files — the login session already covers it; delete still asks for the password
- Password moved out of the repo (it's public) into a gitignored `.env` file; docker-compose reads `${APP_PASSWORD}` from it — see `.env.example`

---

## [0.365] - 2026-07-05

### Security — server-side authentication
- All routes except `/` and `/api/login` now require a logged-in Flask session — previously every API endpoint (including library delete and uploads) was open; only the browser checked the password, which was unsafe with the app exposed at ledmerger.planet4.nu
- New `/api/login` endpoint sets a 90-day session cookie; login overlay now authenticates against the server and no longer contains the password in page source
- Password configurable via `APP_PASSWORD` env var (docker-compose); session secret from `SECRET_KEY` env var or auto-generated key persisted in the library volume
- Rename/delete password prompts now validate against the server instead of a hardcoded string

---

## [0.364] - 2026-07-05

### Library / Login
- Password prompts (login, rename, delete) now accept the password case-insensitively and ignore surrounding whitespace — "Wrong password" no longer triggers on e.g. lowercase input

---

## [0.363] - 2026-07-05

### LED Preview — Arena view alignment
- Zone coordinates re-measured pixel-exactly from the painted strip colors in layout.png
- Videos are now drawn with a 4-corner perspective mapping (sliced affine) instead of a single affine transform — the old method could not hit the bottom-right corner of the trapezoid zones (Media was ~34px off)
- Outward expansion reduced 5% → 2% and overlay opacity 0.92 → 1.0, so content covers the painted strips exactly without tint bleed

---

## [0.362] - 2026-07-05

### Removed
- Auto-render scheduler removed entirely (won't be used) — backend scheduler thread, `/api/autogen/*` routes, Settings tab, and "Auto Generated" library category
- Obsolete TODO.md (its only item was the scheduler preset flow)

### Added (previously undocumented)
- Login overlay on page load (added late April, never changelogged) — note: client-side gate only, not real security

### Housekeeping
- `TEAMSCRAPER_BASE` now configurable via environment variable (docker-compose), defaults to the teamscraper host/port
- Version aligned across README / CLAUDE.md / index.html (were 0.36 / 0.361 mixed)
- Removed stray `{templates,uploads,outputs}` directory (shell brace-expansion typo)
- `.claude/` added to .gitignore; completed roadmap item removed from ROADMAP.md

---

## [0.361] - 2026-04-21

### Custom tab
- Removed autofetch from preset selection — presets are now always static; autofetch infrastructure kept in Settings for future scheduled rendering
- Renamed autofetch default presets (removed "Autofetch" suffix)
- Fixed "Pick team" button overlapping icon (was constrained to 30×30px icon-btn class)

---

## [0.36] - 2026-04-10

### Custom tab
- Autofetch presets — presets with `autofetch_url` fetch live schedule data when selected; other presets remain static
- Added "Kommande matcher - SSL Dam Autofetch" and "Kommande matcher - Pixbo Damakademi Autofetch" presets fetching from internal schedule service
- Slot count extended to 7 — new button in the Slots row, grid and all logic updated
- Fixed generate and preview-render only processing 3 slots regardless of slot count (was hardcoded `range(3)`, now `range(len(texts))`)
- Backgrounds now saved and restored with presets (was missing — only text/font/color were saved)
- Font name now saved and restored with presets
- Text from autofetch is uppercased and 0 replaced with O automatically

### Library
- Added "Non Stacked" category
- Duration now displayed as m:ss instead of raw seconds

### Players tab
- Batch player list is now editable after import — inline edit number/name, ✕ to remove, ＋ to add rows
- Auto Batch import hint added above batch row with inline icon buttons
- PIXBO TEAMNAME row automatically prepended on any batch import (txt or URL scrape)
- Instructional text cleaned up

### DaVinci Scripts
- README rewritten — crop_led1.1.ps1 clarified as the main script; canvas workflow documented with layout table

---

## [0.35] - 2026-04-03

### Players tab
- Batch import: editable player list after import — inline edit number/name, remove rows with ✕, add new rows with ＋ at the bottom
- Batch import: new "Paste team URL" button (link icon) — paste a stats.innebandy.se team URL to fetch the roster automatically via Playwright/Chromium headless scrape
- New backend route `/api/scrape-roster` using Playwright; Playwright + Chromium added to Docker image

### Arena view (LED Preview)
- Strip coordinates updated to match schematic pixel measurements — much more accurate placement on arena photo

---

## [0.34] - 2026-04-02

### Players tab
- Removed font size slider — hidden from UI, hardcoded to 50% (not user-configurable)
- Removed `* 0.62` size reduction that was added during troubleshooting — preview and render now use same sizing
- Fixed text centering on 192px display — `x` position was using `max(w/2, ...)` which pushed text right; now `max(0, (w-text_w)/2)`
- Reduced font size cap on 192px display (coefficient 1.8 → 1.3) to reduce overflow on long names

### Custom tab
- Output rows now use icon-based UI (preview, download, rename, save to library) — same as Players tab
- Fixed font selection being ignored in render — was hardcoded to Road Rage regardless of chosen font
- `|||` padding now only applied when font is Road Rage (pipe character is visible in other fonts)
- Font size % now sent to backend and applied in both render and LED preview (was canvas-only)
- Font size max capped at 100% to prevent layout misplacement

### File Merger tab
- Output row now uses icon-based UI (preview, download, rename, save to library)

### LED Preview
- Reordered display rows: Row 1 = 1344+576L, Row 2 = 1728+576R, Row 3 = 192 Media (was previously mixed)

---

## [0.33] - 2026-04-02

### Players tab
- Fixed letter clipping (A, S, E) — Road Rage has negative left bearing; fixed by wrapping text with invisible `|||` padding characters
- Fixed `y` clipping at top — used `max(0,(h-text_h)/2)` to prevent text rendering above frame edge during wobble peak
- Font size % slider now actually applied to render (was only affecting canvas preview)
- Player number is now optional to skip number phase; batch import skips `#` prefix for non-numeric "numbers" (e.g. team name PIXBO)
- Batch LED preview now shows all players concatenated, not just the first
- Output file rows now show duration, MB, and icon buttons (preview, download, rename, save to library)
- Library-style save added to individual batch player outputs

### Custom tab
- Same `|||` invisible padding fix applied to prevent letter clipping

### Library tab
- Categories collapsed by default with chevron toggle
- File count shown per category when collapsed

### UI / info boxes
- Added batch import format info text (shown after file load)
- Added stats.innebandy.se link button next to batch import
- Added Road Rage zero tip to Players info box
- Replaced batch info box with plain text to fix layout breaking

---

## [0.32] - 2026-03-31

### Project files
- Added `ROADMAP.md` with planned improvements and ideas
- Added `davinciscripts/` folder with PowerShell crop script and README
- Inter font replacing Noto Sans across the UI

---

## [0.31] - 2026-03-29

### Library improvements
- Per-file editable description (saved in metadata.json)
- Video duration shown in seconds next to filename
- ▶ Preview button opens stacked file in a video modal
- Category selector per file — moves file to new category on change
- Delete requires password "Pixbo"
- Categories expanded: Commercial, SSL Players Men/Women, JAS Men/Women, Players Boys/Girls
- Tab info boxes added to all tabs
- Email contact added to header

---

## [0.3] - 2026-03-29

### Library tab
- New Library tab for storing and sharing finished stacked MP4 files
- Categories: Event, General, Special, Players — Men, Players — Women
- Upload MP4 files per category directly from the browser
- Download any file with one click
- Library stored in `data/library/` (volume-mounted, survives rebuilds)
- Daily cleanup: uploads and outputs are automatically deleted at midnight

---

## [0.23] - 2026-03-28

### Background Directory Restructure
- Moved 1344px backgrounds to `data/backgrounds/1344/`, 1728px to `data/backgrounds/1728/`
- Added `BG_DIR_1344` / `BG_DIR_1728` constants and `/api/assets/backgrounds1344` + `/api/assets/backgrounds1728` routes
- Custom tab now fetches each width's library from its own endpoint — no more filename-based filtering
- `select-bg` checks both subdirs; stream security allows both new paths
- Updated `.gitignore` red cloud exception paths to match new locations

---

## [0.22] - 2026-03-28

### Custom Tab
- Slots expanded from 4 to 6 — slots 4–6 shown as a second row of 3 columns
- Fixed text clipping on narrow displays (192px) — font size now capped by display width
- Fixed pop-wobble clipping left edge — drawtext x/y clamped to `max(0, (w-text_w)/2)`
- Fixed slot 4+ not appearing in timing preview or LED preview — revealed slots restore default 2s duration

---

## [0.21] - 2026-03-28

### Custom Tab
- **Pop-wobble effect** added to all text slots — same damped oscillation as Players tab (`base*(1+0.35*exp(-8*t)*cos(12*t))`), with a 0.2s fade-in per slot
- **Slot count selector** (1–4) added to "02 — Custom Text" header — hides unused slot columns and zeroes their duration so they don't render

---

## [0.2] - 2026-03-28

### UI Redesign
- Replaced fonts **DM Sans** and **Space Mono** with **Noto Sans** and **Noto Sans Mono**
- Lightened dark palette to a cooler blue-gray tone (`#1B1E26` base)
- Section headers changed from small red uppercase caps to bold white normal-case text
- Tabs replaced with pill/segment control style
- CSS custom properties used throughout for theme consistency

### Dark / Light Mode
- Added ☀️/🌙 toggle button in the header
- Preference persisted in `localStorage`, OS `prefers-color-scheme` respected on first visit
- No flash on load — theme applied before render via inline script

### Custom Tab — LED Preview
- LED Preview button now renders real preview clips before opening the preview window (same pattern as Players tab)
- New backend route `/api/custom/preview-render` — renders 4 clips at 25fps, no stacked export
- Fixed `FONTS_DIR` → `FONT_DIR` typo in preview route

### Other
- GitHub link added to header subtitle
- Red clouds set as default background on all Custom tab screens

---

## [0.12] - 2026-03-27

### Players Tab — Complete Redesign
- Fixed template backgrounds locked to official Pixbo player template files
- Fixed font — always Road Rage, white — no longer selectable
- Pop wobble effect added (`base*(1+0.35*exp(-8*t)*cos(12*t))`)
- 192px font scaling — auto scales down for narrow displays
- Default timing: 2.1s number, 6s total
- LED Preview button renders real clips at 25fps before opening preview
- Export: stacked + all individual files

### Bug Fixes
- Fixed `FONT_PATH` pointing to wrong filename (`RoadRage.ttf` → `Road_Rage.otf`)
- Fixed LED preview being permanently disabled due to missing `bgPath`
- Fixed Road Rage font not loading in canvas preview on tab load

---

## [0.11] - 2026-03-17

### UI Redesign
- Replaced fonts Barlow Condensed / IBM Plex Mono with DM Sans / Space Mono
- Lightened background from pure black to dark grey `#1A1A1F`
- Cleaner, less decorative cards and section headers
- Consistent display color coding across all tabs

### File Merger Tab
- Live canvas preview in "02 — Visual Layout" updates on upload
- Tile mode preview rewritten to draw correctly onto canvas

### Custom Tab
- Longside Left and Right 576px merged into one unified section — always same content
- Removed separate Longside Right selector

### Tile Mode Fix
- Images now scale to 64px height first before tiling
- Fixes crash with square or portrait images in tile mode

---

## [0.1] - 2026-03-05

### Initial stable release

- Upload files for all 5 displays: Shortside (1344px), Longside Left (576px), Longside Center (1728px), Longside Right (576px), Media (192px)
- Tile mode per display with per-slot upload
- Players tab: number fades to name, configurable timing, pop-wobble, canvas preview
- Custom tab: per-display text slots (3), font/color/size controls, timing preview
- Stacked 1600×1200px export (50fps, h264/yuv420p) + individual files per display
- Layout matches After Effects / ledventure.org reference exactly
- Arena LED layout diagram modal
- Live LED preview window
- Docker deployment

---

## [0.x] - 2026-02-26 to 2026-03-04

### Development / pre-release

- Analyzed reference AE project and export to determine exact row layout
- Confirmed display sizes and 576 content appearing in 3 strip positions
- Built and iterated ffmpeg filter_complex
- Fixed merge, preview, scaling and rendering issues
