# LED Merger — Docker Web App

Web interface for merging 5 LED rink display files into one Sedna-compatible MP4.

## Folder structure

```
LedMerger/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/
│   └── index.html
└── data/
    ├── uploads/
    ├── outputs/
    ├── backgrounds/
    │   ├── media_192/
    │   └── 576_variants/
    └── fonts/
```

## Running with Docker Compose

```bash
# Build and start
docker compose up -d --build

# Open in browser
http://localhost:5000

# Or from another machine on your network:
http://<your-server-ip>:5000
```

## Stopping

```bash
docker compose down
```

## Updating the app

```bash
docker compose up -d --build
```

## Display configuration

| Display | Width | Height |
|---------|-------|--------|
| Display 1 — Centre Main | 1334px | 64px |
| Display 2 — Left Side   |  576px | 64px |
| Display 3 — Back        | 1728px | 64px |
| Display 4 — Right Side  |  576px | 64px |
| Display 5 — End Small   |  192px | 64px |

## Merge modes

- **Stacked** — All 5 clips side-by-side horizontally → one 4406×64px video
- **Sequential** — Clips play one after another in time → standard resolution video

## Supported input formats

MP4, MOV, AVI, GIF, PNG, JPG/JPEG

- Static images are looped for 5 seconds
- GIFs are looped for 10 seconds
- All inputs are scaled and padded to exact display dimensions
