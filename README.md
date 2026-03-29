# LedMerger — Pixbo LED Rink Content Creator

A web-based tool for creating and merging LED rink content for Wallenstam Arena (Pixbo Floorball). Produces stacked MP4 files compatible with the Sedna LED controller.

## What it does

- **File Merger** — Upload individual video/image files for each display zone and merge them into one stacked 1600×1200px MP4
- **Players** — Generate branded player introduction videos using fixed Pixbo templates with Road Rage font and pop-wobble animation
- **Custom** — Create custom text animations for any display zone with configurable backgrounds and timing

All tabs produce a stacked 1600×1200px export matching the After Effects / ledventure.org reference layout, plus individual files per display.

## Display layout

| Display | Width | Height |
|---------|-------|--------|
| Shortside | 1344px | 64px |
| Longside Left | 576px | 64px |
| Longside Center | 1728px | 64px |
| Longside Right | 576px | 64px |
| Media | 192px | 64px |

The stacked export folds all displays into a 1600px wide canvas across 5 rows (320px content + black padding to 1200px), matching the physical LED strip wiring at the arena.

## Folder structure

```
ledmerger/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/
│   ├── index.html
│   └── led_preview.html
└── data/
    ├── uploads/          — temporary upload storage
    ├── outputs/          — generated video files
    ├── backgrounds/
    │   ├── 1728/         — 1728px backgrounds (Longside Center)
    │   ├── 1344/         — 1344px backgrounds (Shortside)
    │   ├── 576_variants/ — 576px variant backgrounds (Players/Custom)
    │   ├── media_192/    — 192px media backgrounds
    │   └── layout.png    — arena layout reference image
    └── fonts/            — custom font files (.ttf, .otf)
```

## Player template files

The Players tab requires these fixed template files. **The filenames are hardcoded — do not rename them.**

```
data/backgrounds/1728/players-template-1728.mp4
data/backgrounds/1344/players-template-1344.mp4
data/backgrounds/576_variants/players-template-576.mp4
data/backgrounds/media_192/players-template-192.mp4
```

All other files in `1728/` and `1344/` are freely renameable — they only appear as dropdown options in the UI.

## Running with Docker

```bash
# Build and start
sudo docker compose up -d --build

# Open in browser
http://localhost:5000

# From another device on the network
http://<server-ip>:5000
```

## Updating

After changing any file:
```bash
sudo docker compose up -d --build
```

Then hard refresh the browser (Ctrl+Shift+R).

## Cleaning up output files

```bash
rm -f data/outputs/*.mp4
rm -f data/uploads/*
```

## Supported input formats

MP4, MOV, AVI, GIF, PNG, JPG/JPEG

## Notes

- Longside Left and Right should use the same source file in stacked exports to avoid visible cuts on the physical displays
- The Players tab uses Road Rage font and white text — fixed and not configurable
- Default player timing is 2.1s number + 3.9s name = 6s total (standard Pixbo lineup time)
