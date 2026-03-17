# Changelog

## [1.1.0] - 2026-03-17

### UI Redesign
- Replaced font **Barlow Condensed** with **DM Sans** for a cleaner, more modern look
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

### Players Tab
- No functional changes

### Custom Tab (Tab 3)
- **Longside Left and Right 576px** merged into a single unified section
- One background selector and one text input section controls both Left and Right
- Left and Right always use identical content in the stacked export — enforced automatically
- Longside Right canvas and timeline row hidden (kept for JS compatibility)
- Removed separate `selectCustom576Right` function

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
- `build_stacked_export` function untouched

---

## [1.0.0] - 2026-03-05

- Initial stable release
- File Merger tab with 5 display inputs and tile mode
- Players tab with background, font, number/name animation
- Custom tab with per-display text slots
- Stacked 1600×1200px export matching AE/ledventure LED strip layout
- Individual display exports for all 5 displays
- Live LED preview window
- Arena layout diagram modal
