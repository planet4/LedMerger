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
- **Presets save background selections** — currently presets only save text and timing, not which background is selected

---

## General

- **Auto-named output files** — output filenames are UUIDs; auto-naming from player name or preset name would make them easier to identify without opening
- **Output file TTL** — daily midnight cleanup could delete files mid-session; a longer TTL or "keep" flag would prevent accidental loss
- **Mobile / tablet layout** — the UI is desktop-only; a basic responsive layout for use in the arena on a tablet

---

## LED Preview

- **Timeline scrubbing** — no way to jump to a specific time; can only sync to t=0 or let it play
- **Arena view recalibration** — zone coordinates are hardcoded percentages; if layout.png is updated they need manual adjustment

---

## DaVinci Scripts

- More helper scripts for preparing content (crop, scale, format conversion)
