# Changelog

All notable changes to the Pixbo LED Merger project are documented here.

Version scheme: `0.1` = initial, `0.11` / `0.12` = incremental updates, `0.2` = major change.

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
