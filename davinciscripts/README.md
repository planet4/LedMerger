# DaVinci Scripts

Helper scripts for preparing LED display content exported from DaVinci Resolve.

---

## crop_led1.1.ps1 — Main script

The primary script for day-to-day use. When you export individual display files from DaVinci — for example player intros, goal animations, or other events — place them all in a folder and run this. It batch crops every MP4 in that folder down to the required 64px height. DaVinci Resolve cannot export below 256px, so this step is always needed.

### What it does

1. Backs up all original files to a `_ORIGINALS_BACKUP` subfolder before touching anything
2. Detects the target width from the filename — files must contain `192`, `576`, `1344`, or `1728` in the name (others are skipped)
3. Checks current height via ffprobe — already 64px files are skipped
4. Crops each file to the correct dimensions:
   - Height always cropped to 64px
   - Y offset is 96px if source is ≥160px tall, otherwise 0 (center crop fallback)
   - X offset is 32px for 192px-wide files, 0 for all others
5. Replaces the original file in-place with the cropped version

### Usage

1. Place the script in the same folder as your exported MP4 files
2. Open PowerShell in that folder
3. Run: `.\crop_led1.1.ps1`

### Requirements

- [ffmpeg](https://ffmpeg.org/) must be available in your system PATH
- Files must be named with their display width (e.g. `players-1728.mp4`, `goal-576.mp4`, `intro-1344.mp4`)

---

## crop_led4224.ps1 + slice_canvas.ps1 — Canvas workflow

Use these two scripts together when you export content as a single wide 4224×256 canvas from DaVinci — with all four displays laid out side by side — instead of as individual files.

**Step 1 — crop_led4224.ps1:** Crops the 4224×256 export down to 4224×64 (center crop, y offset 96px).

**Step 2 — slice_canvas.ps1:** Slices the 4224×64 strip into four individual display files at the correct x offsets. The 192px Media display is out of scope and must be handled separately.

### Display layout in the 4224px canvas

| Display         | Width  | X offset |
|-----------------|--------|----------|
| Shortside       | 1344px | 0        |
| Longside Left   | 576px  | 1344     |
| Longside Center | 1728px | 1920     |
| Longside Right  | 576px  | 3648     |

### Usage

1. Place both scripts in the same folder as your exported MP4 file
2. Open PowerShell in that folder
3. Run: `.\crop_led4224.ps1` — outputs `[originalname]_64px.mp4`
4. Run: `.\slice_canvas.ps1` — outputs four individual display files

### Output format (both scripts)

- Codec: H.264 (libx264), CRF 16, yuv420p
