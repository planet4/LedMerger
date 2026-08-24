# Roadmap

Ideas and planned improvements for LedMerger. No fixed timeline — just a place to track what could be better.

---

## Library

- **Search / filter** — the library will become hard to navigate as it grows; a text filter or tag system would help
- **File ordering** — no way to reorder files within a category
- **Description in collapsed view** — description field exists per file but isn't visible when category is collapsed

---

## Players tab

- **CSV / spreadsheet import** — accept CSV export from Excel or Google Sheets for batch import, more practical for team staff
- **Stacked preview before download** — currently individual clips are previewable but not the combined stacked export
- **Batch progress per player** — single progress bar covers all players; per-player status would be clearer for large batches

---

## Custom tab

- **Text effect selector** — global effect dropdown under Font (section 01), applied to all displays. Options: Wobble (default, current behavior), Fade, Slide Up, Slide Down. Implemented as a parameter to `_text_vf` — low risk, no structural changes needed.
- **Per-display font and color** — all displays share the same font/color; per-display control would allow e.g. different color on Media 192
- **Copy timing to all displays** — no shortcut to sync slot durations across displays when they should all loop at the same length

---

## General

- **Auto-named output files** — output filenames are UUIDs; auto-naming from player name or preset name would make them easier to identify without opening
- **Output file TTL** — daily midnight cleanup could delete files mid-session; a longer TTL or "keep" flag would prevent accidental loss
- **Mobile / tablet layout** — the UI is desktop-only; a basic responsive layout for use in the arena on a tablet

---

## LED Preview

- **Timeline scrubbing** — no way to jump to a specific time; can only sync to t=0 or let it play
- **Arena view recalibration** — zone coordinates are hardcoded percentages; if layout.png is updated they need manual adjustment
- **Arena view for library files** — the LED/arena preview only works from the Players tab, which has the 5 separate display clips. The Library only stores the stacked 1600×1200 file, so its preview is a plain video player. Options discussed: (A) add an "LED" play button next to the normal play button that opens `led_preview.html` in a new **stacked mode** which slices the 5 display regions back out of the stack (inverse of `build_stacked_export`'s row layout) — no extra storage, but the crop math must exactly mirror the stack layout; (B) also save the 5 individual clips alongside the stacked file so `openLedPreview` can be reused directly (≈6× storage). Recommended: A. Low risk — does not touch `build_stacked_export`; main cautions are not regressing the shared Players preview (gate behind a param) and getting crop offsets right (cosmetic if wrong).
- **Save the LED/arena preview** — export what the arena view shows as a shareable artifact: a static arena thumbnail (easy, grab a canvas frame) or an animated arena clip (record the canvas via MediaRecorder — webm/quality caveats). Cleanest captured from the Players LED Preview where the arena renderer already has the individual clips.

---

## DaVinci Scripts

- More helper scripts for preparing content (crop, scale, format conversion)
