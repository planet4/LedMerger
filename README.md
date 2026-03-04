# LED Merger — A Customized LED rink content creator for Pixbo Floorball

This app is customized to work with the setup at Wallenstam Arena. It will either merge 5 LED rink display files into one Sedna-compatible MP4, create branded player files or in the future any other custom text.
The main usage for this app is to create one mp4 file of many small. By doing this it will be a stacked file in Sedna.

## Folder structure

Put your own fonts in fonts dir. Put your custom backgrounds in the backgrounds dir.

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

## Supported input formats

MP4, MOV, AVI, GIF, PNG, JPG/JPEG

## Usage

# File Merger
# Players


