# DaVinci Scripts

Helper scripts for preparing LED display content that DaVinci Resolve cannot handle natively.

---

## crop_led1.1.ps1

**Platform:** Windows (PowerShell + ffmpeg)

Batch crops MP4 files exported from DaVinci Resolve down to the required 64px height for the Sedna LED controller displays.

### What it does

1. Backs up all original files to a `_ORIGINALS_BACKUP` subfolder before touching them
2. Detects the target width from the filename — files must contain `192`, `576`, `1344`, or `1728` in the name (files not matching any of these are skipped)
3. Checks the current height using ffprobe — if already 64px, the file is skipped
4. Crops each file to the correct dimensions using ffmpeg:
   - Height is always cropped to 64px
   - Y offset is 96px if the source is ≥160px tall, otherwise 0 (center crop fallback)
   - X offset is 32px for 192px-wide files, 0 for all others
5. Replaces the original file with the cropped version in-place

### Output format

- Codec: H.264 (libx264)
- CRF: 16 (high quality)
- Pixel format: yuv420p

### Usage

1. Place the script in the same folder as your exported MP4 files
2. Open PowerShell in that folder
3. Run: `.\crop_led1.1.ps1`
4. Press Enter when done

### Requirements

- [ffmpeg](https://ffmpeg.org/) must be available in your system PATH
- Files must be named with their display width (e.g. `intro-1728.mp4`, `goal-576.mp4`)
