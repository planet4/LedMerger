# Changelog

All notable changes to the Pixbo LED Merger project are documented here.

---

## [1.1.0] - 2026-03-17

### UI Redesign
- RReplaced font **Barlow Condensed** with **DM Sans** for a cleaner, more modern look
- Replaced monospace font **IBM Plex Mono** with **Space Mono**
- Lightened background from pure black `#0C0C0C` to dark grey `#1A1A1F`
- Cards and section headers now use a cleaner, less decorative style
- Tabs redesigned to be smaller and simpler
- Red accent color `#CC1020` retained throughout
- Consistent display color coding across all tabs:
  - Longside Center — Green `#1A4731`
  - Shortside — Red `#7B1520`
  - Longside Left — Blue `#1E3A5F`
  - Longside Right — Yellow `#7A5C00`
  - Media 192px — Purple `#4A2060`

### File Merger Tab
- **02 — Visual Layout** now shows a live canvas preview matching the Players tab style
- Preview updates instantly when files are uploaded
- Tile mode preview rewritten to draw correctly onto canvas
- Tile slot thumbnails now use `object-fit:contain` to correctly show image proportions

### Custom Tab
- **Longside Left and Right 576px** merged into a single unified section
- One background selector and one text input section controls both Left and Right
- Left and Right always use identical content in the stacked export — enforced automatically
- Removed separate Longside Right selector and timeline row

### Info Boxes
- Added warning box on **File Merger** and **Players** tabs advising to use the same file for Longside Left and Longside Right in stacked exports
- No warning on Custom tab since Left/Right are now unified automatically

### Tile Mode Fix
- Tile images now scale to **64px height first** (keeping aspect ratio) before tiling
- If image is narrower than tile width after scaling, it is centered with black padding
- If image is wider, it is cropped from center
- Fixes crash when using square or portrait images (e.g. 1280×1280) in tile mode
- Canvas preview updated to match the same height-first scaling logic

### Export (Unchanged)
- All three tabs produce identical 1600×1200px stacked exports
- Layout matches the AE/ledventure reference exactly

---

## [1.0.0] - 2026-03-05

### Initial stable release

#### File Merger Tab
- Upload files for all 5 displays: Shortside (1344px), Longside Left (576px), Longside Center (1728px), Longside Right (576px), Media (192px)
- Tile mode for each display — repeat a file N times across the display width
- Per-tile slot upload (different image per tile position)
- Live canvas preview for each display in **02 — Visual Layout**
- Stacked 1600×1200px export + individual file per display

#### Players Tab
- Select background video from library
- Select font from library (Road Rage, Barlow Condensed, Oswald, etc.)
- Select 576px variant background for Longside Left and Right independently
- Select Media 192px background
- Enter player number and name
- Number fades out, name fades in with configurable timing
- Live visual layout preview with canvas rendering
- Timing preview bar showing number/name durations
- Stacked 1600×1200px export + individual file per display

#### Custom Tab
- Per-display background selection (library or black)
- Per-display text slots (up to 3 slots per display, each with configurable duration)
- Font selection shared across all displays
- Font size and color controls
- Live visual layout preview
- Timing preview bar per display
- Stacked 1600×1200px export + individual file per display

#### Core Export Engine
- Stacked export: 1600×1200px, 50fps, h264/yuv420p
- Layout matches the After Effects / ledventure.org reference template exactly:
  - Row 1 (y=0): Shortside 1344px
  - Row 2 (y=64): Shortside tail 384px + Longside Left 576px
  - Row 3 (y=128): Longside Center 1728px (clipped to 1600)
  - Row 4 (y=192): Longside Center tail 768px + Longside Right 576px
  - Row 5 (y=256): Longside Left tail 384px + Media 192px
  - Rows 6-19: black padding to 1200px
- All clips looped to match longest duration before merging
- Individual exports at native display sizes

#### Other Features
- Arena LED layout diagram modal with color-coded display map
- Live LED preview window (opens in separate browser tab)
- Docker deployment with docker-compose
- Background and font libraries loaded from data/ folder
- 576px variant library for Players and Custom tabs
- Media 192px library

---

## [0.x] - 2026-02-26 to 2026-03-04

### Development history (pre-release)

- Investigated After Effects project file (Pixbo-Mall-fran_ledventure-org.aep) to determine exact export format
- Analyzed reference export Timeout_Pixbo.mp4 pixel-by-pixel to confirm row layout
- Discovered displays wrap across rows at 1600px boundary
- Confirmed Shortside is 1344px (not 1334px as initially assumed)
- Confirmed 576 content appears in 3 positions in the strip — same source used for rows 2, 4 and 5
- Built and iterated on ffmpeg filter_complex with split filters for reused inputs
- Added separate Longside Left and Right selectors with independent state
- Added Media 192px background selector with separate folder
- Fixed merge width mismatch
- Fixed LED preview to show all 5 displays
- Rebuilt visual layout preview with 5 named blocks and proportional widths
- Fixed 192px rendering — text overlay, correct scale, no thin-line artifact
- Fixed 576 clips — background-only (no player text on side panels)
- Added Media 192px to Players tab with number/name text overlay
- Fixed filter_complex to split reused inputs (was causing silent hang on merge)
- Tested and verified output against reference video
