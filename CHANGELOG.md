# Changelog

All notable changes to the Pixbo LED Merger project are documented here.

Version scheme: `0.1` = initial, `0.11` / `0.12` = incremental updates, `0.2` = major change.

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
