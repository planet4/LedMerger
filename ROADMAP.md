# Roadmap

Ideas and planned improvements for LedMerger. No fixed timeline — just a place to track what could be better.

---

## Library

- **Rename files** — rename an uploaded file without having to delete and re-upload
- **File size** — show file size next to duration
- **Search / filter** — filter files by name or description, useful once the library grows
- **Upload progress** — show a progress bar for large file uploads

## Players tab

- **Batch lineup** — paste a full lineup (number + name per line) and generate all player clips in one go, instead of one at a time
- **Save to Library** — after generating a player clip, offer a button to save it directly to the Library (e.g. SSL Players Men/Women) without downloading and re-uploading
- **Fetch players from stats.innebandy.se** — automatically import a team's roster by pasting a link (e.g. `https://stats.innebandy.se/sasong/43/serie/43161/`) so you don't have to type numbers and names manually

## Custom tab

- **Save/load presets** — save a full Custom tab setup (backgrounds, text, timing) and reload it in a later session
- **Example template** — pre-fill the tab with example text, durations, and a layout on first load so users can see how it works before building their own

## General

- **Recent exports** — a small list of files currently in `data/outputs/` so you can re-download without regenerating
- **Manual cleanup** — a button to clear outputs and uploads on demand, in addition to the automatic midnight cleanup
- **Mobile layout** — the UI is desktop-only; a basic responsive layout for tablet use in the arena
- **UI polish** — replace text labels on action buttons with icons where it makes sense, to reduce visual clutter
- **Button style consistency** — review and unify button styles; reduce overuse of pill/rounded shapes in favour of a cleaner, more consistent look

## DaVinci Scripts

- More helper scripts for preparing content (crop, scale, format conversion)
