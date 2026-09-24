# Roadmap

Ideas and planned improvements for LedMerger. No fixed timeline — just a place to track what could be better.

---

## Library

- **Search / filter** — the library will become hard to navigate as it grows; a text filter or tag system would help
- **File ordering within a category** — categories themselves now auto-sort by file count, but there's still no way to manually reorder the files *within* one category
- **Description in collapsed view** — description field exists per file but isn't visible when category is collapsed

---

## Players tab

- **CSV / spreadsheet import** — accept CSV export from Excel or Google Sheets for batch import, more practical for team staff
- **Stacked preview before download** — currently individual clips are previewable but not the combined stacked export
- **Batch progress per player** — single progress bar covers all players; per-player status would be clearer for large batches
- **Batch mode doesn't render individual per-display clips** — unlike single-generate/Custom, batch (both combined and per-player) never saves the 5 per-display source clips, so batch-saved library files always hit LED Preview's slower extraction fallback instead of getting an instant sidecar at save time. Would need `lineup_batch_worker` changes to copy those clips per player the way `lineup_generate`/`custom_generate` already do.
- **Pick team without teamscraper** — fetch Pixbo rosters directly from the innebandy JSON API instead of proxying teamscraper, so Pick team keeps working when teamscraper is down. **Pixbo teams only.** Rough plan:
  - Only `/api/scheduler-teams` and `/api/scheduler-roster/<id>` in `app.py` change. Keep their response shape (`team_id`, `team_name`, `players[].number/name`) so the frontend needs no changes.
  - **Teams come and go during the year**, so the team list must not need a code change or rebuild. Either a JSON file under `data/library/` (id + display name), or auto-discovery through the Pixbo associations (`/seasons/<s>/associations/<id>/teams`, cached) with display-name overrides. The API's own names are unusable for some teams: Herr and Dam are both just "Pixbo IBK". Only accept team IDs from that list.
  - Season is set by hand each autumn through an env var (e.g. `INNEBANDY_SEASON`). No rebuild needed.
  - Token from the `startkit` endpoint, valid 30 min. Cache it with a lock.
  - Re-sort to match today's order: no number first, then number, then name.
  - Player exclusions go in a gitignored data file, never in code.
  - Store the last good roster per team under `data/library/`, not `outputs/` (wiped nightly). Serve it when the API fails.
  - Before switching, diff the new routes against teamscraper for every team. Expected difference: the scraper appends a captain "K" to some names, and the API doesn't.
  - Then remove `TEAMSCRAPER_BASE`. The API is unofficial, so keep calls low (live on click is fine).

---

## Custom tab

- **Text effect selector** — global effect dropdown under Font (section 01), applied to all displays. Options: Wobble (default, current behavior), Fade, Slide Up, Slide Down. Implemented as a parameter to `_text_vf` — low risk, no structural changes needed.
- **Per-display font and color** — all displays share the same font/color; per-display control would allow e.g. different color on Media 192
- **Copy timing to all displays** — no shortcut to sync slot durations across displays when they should all loop at the same length

---

## General

- **Auto-named output files** — Players (single + batch) and Custom already name outputs from player/team name; File Merger's stacked output is still a bare `sedna_stacked_<uuid>.mp4` with no way to know what it is without opening it
- **Output file TTL** — `_daily_cleanup` (app.py) wipes `data/outputs`/`data/uploads` entirely at midnight, so anything generated but not saved to the Library is lost overnight, and a long session running past midnight can have files vanish mid-use. A longer TTL (e.g. delete older than 48h rather than everything) or a "keep" flag would prevent accidental loss.
- **Mobile / tablet layout** — the UI is desktop-only; a basic responsive layout for use in the arena on a tablet

---

## LED Preview

- **Timeline scrubbing** — Merged File mode has it for free (native `<video controls>`); Arena View and Separate Files still can't jump to a specific time, only sync to t=0 or let it play
- **Arena view recalibration** — zone coordinates are hardcoded percentages; if layout.png is updated they need manual adjustment
- **Save the LED/arena preview** — export what the arena view shows as a shareable artifact: a static arena thumbnail (easy, grab a canvas frame) or an animated arena clip (record the canvas via MediaRecorder — webm/quality caveats). Cleanest captured from the Players LED Preview where the arena renderer already has the individual clips.
- **Arena View / Separate Files for "Non Stacked" files** — those are raw single-display clips with no 5-way split, so only Merged File applies today (graceful, not broken — just limited). Would need to know *which* display a given raw clip is for (currently unknowable — no metadata, and filenames aren't a reliable convention) to place it correctly in Arena View.

---

## DaVinci Scripts

- More helper scripts for preparing content (crop, scale, format conversion)
