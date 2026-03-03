"""
Sedna LED Rink Display Merger — Flask Web App
"""

import os
import uuid
import shutil
import tempfile
import subprocess
import threading
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file, abort

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

UPLOAD_DIR  = Path("/app/uploads")
OUTPUT_DIR  = Path("/app/outputs")
FONT_DIR    = Path("/app/fonts")
BG_DIR        = Path("/app/backgrounds")
MEDIA192_DIR  = Path("/app/backgrounds/media_192")
for _d in [UPLOAD_DIR, OUTPUT_DIR, FONT_DIR, BG_DIR, MEDIA192_DIR]:
    _d.mkdir(exist_ok=True)

DISPLAYS = [
    {"id": 0, "name": "Shortside",        "width": 1344, "height": 64},
    {"id": 1, "name": "Longside Left",    "width":  576, "height": 64},
    {"id": 2, "name": "Longside Center",  "width": 1728, "height": 64},
    {"id": 3, "name": "Longside Right",   "width":  576, "height": 64},
    {"id": 4, "name": "Media",            "width":  192, "height": 64},
]

# job_id -> {"status": "...", "progress": "...", "output": "..."}
jobs = {}


def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace")[-3000:])


def normalise(src: Path, dst: Path, w: int, h: int, fps: str):
    """Convert any input to a normalised mp4 at exact w×h dimensions."""
    ext = src.suffix.lower()
    if ext in (".png", ".jpg", ".jpeg"):
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", "5",
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                   f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black",
            "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
        ]
    elif ext == ".gif":
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src), "-t", "10",
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                   f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black",
            "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                   f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black",
            "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(dst),
        ]
    run_cmd(cmd)


def normalise_to_tile(src: Path, dst: Path, tile_w: int, tile_h: int,
                      duration: float, fps: str):
    """Normalise one source clip/image to tile_w×tile_h at given duration."""
    ext = src.suffix.lower()
    if ext in (".png", ".jpg", ".jpeg"):
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", str(duration),
            "-vf", f"scale={tile_w}:{tile_h}:force_original_aspect_ratio=decrease,"
                   f"pad={tile_w}:{tile_h}:(ow-iw)/2:(oh-ih)/2:color=black",
            "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src),
            "-t", str(duration),
            "-vf", f"scale={tile_w}:{tile_h}:force_original_aspect_ratio=decrease,"
                   f"pad={tile_w}:{tile_h}:(ow-iw)/2:(oh-ih)/2:color=black",
            "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(dst),
        ]
    run_cmd(cmd)


def tile_clip(src: Path, dst: Path, tile_w: int, tile_h: int,
              tiles: int, duration: float, fps: str,
              slot_paths: list = None):
    """
    Build a tiled clip. Each tile can have its own source (slot_paths[i]).
    Falls back to src for any slot without a specific path.
    slot_paths: list of Path or None per slot.
    """
    tmp_dir = dst.parent
    tile_srcs = []
    for ti in range(tiles):
        sp = (slot_paths[ti] if slot_paths and ti < len(slot_paths)
              and slot_paths[ti] else src)
        tile_out = tmp_dir / f"_tile_{dst.stem}_{ti}.mp4"
        normalise_to_tile(Path(sp), tile_out, tile_w, tile_h, duration, fps)
        tile_srcs.append(tile_out)

    # hstack all tile clips
    inputs = []
    for p in tile_srcs:
        inputs += ["-i", str(p)]
    run_cmd([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", f"hstack=inputs={tiles}",
        "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(dst),
    ])
    for p in tile_srcs:
        p.unlink(missing_ok=True)



def build_stacked_export(shortside, longsideleft, longsidecenter, longsideright, media, output_path, fps, tmp):
    """Build 1600x1200 stacked export matching the AE ledventure layout.
    
    Layout (5 rows x 64px, 1600px wide, rest black to 1200px):
    Row 1 (y=0):   Shortside      pixels 0→1344      x=0
    Row 2 (y=64):  Shortside      pixels 960→1344     x=0   (last 384px)
                   LongsideLeft   pixels 0→576        x=384
    Row 3 (y=128): LongsideCenter pixels 0→1600       x=0   (first 1600 of 1728)
    Row 4 (y=192): LongsideCenter pixels 960→1728     x=0   (last 768px)
                   LongsideRight  pixels 0→576        x=768
    Row 5 (y=256): LongsideLeft   pixels 192→576      x=0   (last 384px, same src as left)
                   Media          pixels 0→192        x=384
    """
    fc = (
        # Split reused inputs first
        "[0]split=2[s0a][s0b];"
        "[1]split=2[s1a][s1b];"
        "[2]split=2[s2a][s2b];"
        # Black canvas
        "color=black:size=1600x1200:rate={fps}:duration=99999[canvas];"
        # Row 1: Shortside full 1344px at x=0,y=0
        "[s0a]crop=1344:64:0:0[s_full];"
        "[canvas][s_full]overlay=x=0:y=0:shortest=1[c1];"
        # Row 2a: Shortside last 384px at x=0,y=64
        "[s0b]crop=384:64:960:0[s_tail];"
        "[c1][s_tail]overlay=x=0:y=64[c2];"
        # Row 2b: LongsideLeft full 576px at x=384,y=64
        "[s1a]crop=576:64:0:0[ll_full];"
        "[c2][ll_full]overlay=x=384:y=64[c3];"
        # Row 3: LongsideCenter first 1600px at x=0,y=128
        "[s2a]crop=1600:64:0:0[lc_head];"
        "[c3][lc_head]overlay=x=0:y=128[c4];"
        # Row 4a: LongsideCenter last 768px at x=0,y=192
        "[s2b]crop=768:64:960:0[lc_tail];"
        "[c4][lc_tail]overlay=x=0:y=192[c5];"
        # Row 4b: LongsideRight full 576px at x=768,y=192
        "[3]crop=576:64:0:0[lr_full];"
        "[c5][lr_full]overlay=x=768:y=192[c6];"
        # Row 5a: LongsideLeft last 384px at x=0,y=256
        "[s1b]crop=384:64:192:0[l576_tail];"
        "[c6][l576_tail]overlay=x=0:y=256[c7];"
        # Row 5b: Media full 192px at x=384,y=256
        "[4]crop=192:64:0:0[media_full];"
        "[c7][media_full]overlay=x=384:y=256[out]"
    ).format(fps=fps)

    run_cmd([
        "ffmpeg", "-y",
        "-i", str(shortside),
        "-i", str(longsideleft),
        "-i", str(longsidecenter),
        "-i", str(longsideright),
        "-i", str(media),
        "-filter_complex", fc,
        "-map", "[out]",
        "-r", str(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(output_path),
    ])

def merge_worker(job_id, file_paths, tile_configs, mode, fps, output_path):
    """
    file_paths   : list of 5 server file paths
    tile_configs : list of 5 dicts — either
                   {"tiled": False}  or
                   {"tiled": True, "tiles": N, "duration": float}
    """
    tmp = Path(tempfile.mkdtemp(prefix="sedna_"))
    try:
        jobs[job_id]["status"] = "running"
        normed = []

        for i, (path, d, tcfg) in enumerate(zip(file_paths, DISPLAYS, tile_configs)):
            jobs[job_id]["progress"] = f"Processing {d['name']} ({i+1}/5)…"
            out = tmp / f"norm_{i}.mp4"

            if tcfg.get("tiled"):
                tiles      = max(2, int(tcfg.get("tiles", 2)))
                duration   = float(tcfg.get("duration", 6))
                tile_w     = d["width"] // tiles
                slot_paths = tcfg.get("slot_paths", [])
                tile_clip(Path(path), out, tile_w, d["height"],
                          tiles, duration, fps, slot_paths=slot_paths)
            else:
                normalise(Path(path), out, d["width"], d["height"], fps)

            normed.append(out)

        jobs[job_id]["progress"] = "Merging clips…"

        if mode == "stacked":
            # Find longest clip duration so all clips can be looped to match
            def probe_duration(p):
                r = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                    capture_output=True, text=True
                )
                try:
                    return float(r.stdout.strip())
                except:
                    return 0.0

            durations = [probe_duration(p) for p in normed]
            max_dur   = max(durations) if durations else 0

            # Loop any clip shorter than max_dur up to max_dur
            looped = []
            for i, (p, dur) in enumerate(zip(normed, durations)):
                if dur < max_dur - 0.05:
                    lp = tmp / f"looped_{i}.mp4"
                    run_cmd([
                        "ffmpeg", "-y",
                        "-stream_loop", "-1", "-i", str(p),
                        "-t", str(max_dur),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        str(lp),
                    ])
                    looped.append(lp)
                else:
                    looped.append(p)

            # Build 1600x1200 stacked export matching AE/ledventure layout
            # displays: 0=shortside, 1=longsideleft, 2=longsidecenter, 3=longsideright, 4=media
            build_stacked_export(
                looped[0], looped[1], looped[2], looped[3], looped[4],
                output_path, fps, tmp
            )
        else:
            list_file = tmp / "concat.txt"
            list_file.write_text("\n".join(f"file '{p}'" for p in normed))
            run_cmd([
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", str(list_file),
                "-r", fps, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                str(output_path),
            ])

        jobs[job_id]["status"] = "done"
        jobs[job_id]["progress"] = "Complete!"
        jobs[job_id]["output"] = str(output_path.name)

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["progress"] = str(e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", displays=DISPLAYS)


@app.route("/api/displays")
def api_displays():
    return jsonify(DISPLAYS)


@app.route("/api/bg-preview")
def bg_preview():
    """Return a mid-point frame from a background file in the BG library."""
    import tempfile as _tf, os as _os
    filename = request.args.get("filename", "")
    src = BG_DIR / filename
    if not src.exists():
        abort(404)
    ext = src.suffix.lower()
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg",
                "webp":"image/webp","gif":"image/gif"}.get(ext.lstrip("."), "image/png")
        return send_file(str(src), mimetype=mime)
    tmp_fd, tmp_path = _tf.mkstemp(suffix=".jpg")
    _os.close(tmp_fd)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
            capture_output=True, text=True
        )
        try:
            seek = float(probe.stdout.strip()) * 0.2
        except:
            seek = 1.0
        run_cmd(["ffmpeg", "-y", "-ss", str(seek), "-i", str(src),
                 "-vframes", "1", "-q:v", "3", tmp_path])
        if Path(tmp_path).stat().st_size > 0:
            return send_file(tmp_path, mimetype="image/jpeg")
        abort(500)
    except:
        abort(500)


@app.route("/api/bg-preview-path")
def bg_preview_path():
    """Return a mid-point frame from any server-side file path (uploaded or library)."""
    import tempfile as _tf
    path = request.args.get("path", "")
    if not path:
        abort(400)
    src = Path(path)
    if not src.exists():
        abort(404)
    ext = src.suffix.lower()
    # For static images, serve directly — no ffmpeg needed
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg",
                "webp":"image/webp","gif":"image/gif"}.get(ext.lstrip("."), "image/png")
        return send_file(str(src), mimetype=mime)
    # For video, extract a frame at 20% in
    tmp_fd, tmp_path = _tf.mkstemp(suffix=".jpg")
    import os; os.close(tmp_fd)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
            capture_output=True, text=True
        )
        try:
            seek = float(probe.stdout.strip()) * 0.2
        except:
            seek = 1.0
        run_cmd(["ffmpeg", "-y", "-ss", str(seek), "-i", str(src),
                 "-vframes", "1", "-q:v", "3", tmp_path])
        if Path(tmp_path).stat().st_size > 0:
            return send_file(tmp_path, mimetype="image/jpeg")
        abort(500)
    except:
        abort(500)


@app.route("/api/stream/<int:display_id>")
def stream_display(display_id):
    """Stream the most recently uploaded file for a display."""
    slot = request.args.get("slot", "")
    if slot != "":
        files = sorted(UPLOAD_DIR.glob(f"*_{display_id}_s{slot}.*"), key=lambda f: f.stat().st_mtime)
        if not files:
            files = sorted(UPLOAD_DIR.glob(f"*_{display_id}.*"), key=lambda f: f.stat().st_mtime)
    else:
        files = sorted(UPLOAD_DIR.glob(f"*_{display_id}.*"), key=lambda f: f.stat().st_mtime)
        files = [f for f in files if "_s" not in f.stem.split(f"_{display_id}")[-1]]
        if not files:
            files = sorted(UPLOAD_DIR.glob(f"*_{display_id}.*"), key=lambda f: f.stat().st_mtime)
    if not files:
        abort(404)
    src = files[-1]
    ext = src.suffix.lower()
    mime_map = {".mp4":"video/mp4",".mov":"video/quicktime",".avi":"video/x-msvideo",
                ".gif":"image/gif",".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg"}
    mime = mime_map.get(ext, "application/octet-stream")
    return send_file(str(src), mimetype=mime, conditional=True)





@app.route("/api/layout-image")
def layout_image():
    """Serve the arena layout reference image if one exists in /app/backgrounds."""
    for ext in [".png", ".jpg", ".jpeg"]:
        for name in ["layout", "arena", "ledlayout", "rink"]:
            p = BG_DIR / f"{name}{ext}"
            if p.exists():
                return send_file(str(p), mimetype=f"image/{ext.strip('.')}")
    abort(404)


@app.route("/api/assets/fonts")
def list_fonts():
    exts = {".ttf", ".otf"}
    fonts = [f.name for f in FONT_DIR.iterdir() if f.suffix.lower() in exts]
    return jsonify(sorted(fonts))


@app.route("/api/assets/font-file/<filename>")
def serve_font(filename):
    """Serve a font file from the fonts directory so browser canvas can use it."""
    path = FONT_DIR / filename
    if not path.exists() or path.suffix.lower() not in {".ttf", ".otf", ".woff", ".woff2"}:
        abort(404)
    mime = "font/otf" if path.suffix.lower() == ".otf" else "font/ttf"
    return send_file(str(path), mimetype=mime)


@app.route("/api/assets/backgrounds")
def list_backgrounds():
    exts = {".mp4", ".mov", ".avi"}
    bgs = [f.name for f in BG_DIR.iterdir() if f.suffix.lower() in exts]
    return jsonify(sorted(bgs))


VARIANTS_DIR = Path("/app/backgrounds/576_variants")

@app.route("/api/assets/576variants")
def list_576_variants():
    VARIANTS_DIR.mkdir(exist_ok=True)
    exts = {".mp4", ".mov", ".avi", ".png", ".jpg", ".jpeg", ".gif"}
    files = [f.name for f in VARIANTS_DIR.iterdir() if f.suffix.lower() in exts]
    return jsonify(sorted(files))


@app.route("/api/assets/media192")
def list_media192():
    MEDIA192_DIR.mkdir(exist_ok=True)
    exts = {".mp4", ".mov", ".avi", ".png", ".jpg", ".jpeg", ".gif"}
    files = [f.name for f in MEDIA192_DIR.iterdir() if f.suffix.lower() in exts]
    return jsonify(sorted(files))


@app.route("/api/lineup/select-576variant", methods=["POST"])
def select_576_variant():
    data     = request.json
    filename = data.get("filename", "")
    path     = VARIANTS_DIR / filename
    if not path.exists():
        return jsonify({"error": "File not found"}), 404
    return jsonify({"ok": True, "path": str(path)})


@app.route("/api/upload/<int:display_id>", methods=["POST"])
def upload(display_id):
    if display_id not in range(len(DISPLAYS)):
        abort(400)
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file"}), 400
    ext = Path(f.filename).suffix.lower()
    allowed = {".mp4", ".mov", ".avi", ".gif", ".png", ".jpg", ".jpeg"}
    if ext not in allowed:
        return jsonify({"error": f"File type {ext} not supported"}), 400
    slot = request.args.get("slot", "")
    uid  = uuid.uuid4().hex
    slot_suffix = f"_s{slot}" if slot != "" else ""
    dest = UPLOAD_DIR / f"{uid}_{display_id}{slot_suffix}{ext}"
    f.save(str(dest))
    return jsonify({"ok": True, "filename": f.filename, "path": str(dest)})


@app.route("/api/merge", methods=["POST"])
def merge():
    data         = request.json
    file_paths   = data.get("files", [])
    tile_configs = data.get("tile_configs", [{"tiled": False}] * len(DISPLAYS))
    mode         = data.get("mode", "stacked")
    fps          = str(data.get("fps", 30))

    if len(file_paths) != len(DISPLAYS):
        return jsonify({"error": "Need exactly 5 file paths"}), 400
    for p in file_paths:
        if not Path(p).exists():
            return jsonify({"error": f"File missing: {p}"}), 400

    job_id   = uuid.uuid4().hex
    out_name = f"sedna_{mode}_{job_id[:8]}.mp4"
    out_path = OUTPUT_DIR / out_name

    jobs[job_id] = {"status": "queued", "progress": "Queued…", "output": None}
    t = threading.Thread(
        target=merge_worker,
        args=(job_id, file_paths, tile_configs, mode, fps, out_path),
        daemon=True,
    )
    t.start()
    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job"}), 404
    return jsonify(job)


@app.route("/api/download/<filename>")
def download(filename):
    path = OUTPUT_DIR / filename
    if not path.exists() or not path.is_file():
        abort(404)
    return send_file(str(path), as_attachment=True)


@app.route("/api/stream")
def stream_file():
    """Stream an uploaded file by server path for in-browser preview."""
    path = request.args.get("path", "")
    if not path:
        abort(400)
    src = Path(path)
    # Security: only allow files inside UPLOAD_DIR or OUTPUT_DIR or VARIANTS_DIR
    allowed = [UPLOAD_DIR.resolve(), OUTPUT_DIR.resolve(), VARIANTS_DIR.resolve(), BG_DIR.resolve(), MEDIA192_DIR.resolve()]
    if not any(src.resolve().is_relative_to(d) for d in allowed):
        abort(403)
    if not src.exists():
        abort(404)
    ext = src.suffix.lower()
    mime_map = {
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime = mime_map.get(ext, "application/octet-stream")
    return send_file(str(src), mimetype=mime, conditional=True)


@app.route("/led-preview")
def led_preview():
    """Serve the LED preview page."""
    return render_template("led_preview.html")


# ── Lineup / Player Cards ─────────────────────────────────────────────────────

LINEUP_DISPLAYS = [
    {"id": 0, "name": "Longside Center", "width": 1728, "height": 64},
    {"id": 1, "name": "Shortside",       "width": 1344, "height": 64},
    {"id": 2, "name": "Media",           "width":  192, "height": 64},
]

FONT_PATH = Path("/app/fonts/RoadRage.ttf")


def lineup_worker(job_id, bg_path, variant_576_left_path, variant_576_right_path, media_192_path, number, name, fps_val, fade_dur, num_dur, total_dur, font_name=""):
    tmp = Path(tempfile.mkdtemp(prefix="lineup_"))
    try:
        jobs[job_id]["status"] = "running"

        chosen_font = FONT_DIR / font_name if font_name else FONT_PATH
        font_arg    = f"fontfile={chosen_font}:" if chosen_font.exists() else ""

        def render_text_clip(w, h, out_path, src_override=None):
            fade_out_start = num_dur - fade_dur
            fade_in_end    = num_dur + fade_dur
            font_size      = int(h * 0.80) if w >= 1000 else int(h * 0.60) if w >= 400 else int(h * 0.50)
            number_text    = f"# {number}"
            name_text      = name.upper()
            txt_number = (
                f"drawtext={font_arg}text='{number_text}':fontcolor=white:"
                f"fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2:"
                f"alpha='if(lt(t,{fade_out_start}),1,"
                f"if(lt(t,{num_dur}),({num_dur}-t)/{fade_dur},0))'"
            )
            txt_name = (
                f"drawtext={font_arg}text='{name_text}':fontcolor=white:"
                f"fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2:"
                f"alpha='if(lt(t,{num_dur}),0,"
                f"if(lt(t,{fade_in_end}),(t-{num_dur})/{fade_dur},1))'"
            )
            run_cmd([
                "ffmpeg", "-y",
                *(  ["-loop","1"] if src_override and src_override.suffix.lower() in (".png",".jpg",".jpeg")
                    else ["-stream_loop","-1"]
                   ),
                "-i", str(src_override if src_override else bg_path),
                "-t", str(total_dur),
                "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                       f"crop={w}:{h},{txt_number},{txt_name}",
                "-r", str(fps_val), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an",
                str(out_path),
            ])

        def render_576_clip(out_path, src_path):
            if src_path and Path(src_path).exists():
                src = Path(src_path)
                ext = src.suffix.lower()
                loop_arg = ["-loop", "1"] if ext in (".png",".jpg",".jpeg") else ["-stream_loop", "-1"]
                run_cmd([
                    "ffmpeg", "-y", *loop_arg, "-i", str(src),
                    "-t", str(total_dur),
                    "-vf", "scale=576:64:force_original_aspect_ratio=increase,"
                           "crop=576:64",
                    "-r", str(fps_val), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an",
                    str(out_path),
                ])
            else:
                run_cmd([
                    "ffmpeg", "-y",
                    "-f", "lavfi", "-i", f"color=black:size=576x64:rate={fps_val}",
                    "-t", str(total_dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(out_path),
                ])

        # Render each size
        jobs[job_id]["progress"] = "Rendering Longside Center (1728)…"
        clip_1728 = tmp / "clip_1728.mp4"
        render_text_clip(1728, 64, clip_1728)

        jobs[job_id]["progress"] = "Rendering Shortside (1344)…"
        clip_1344 = tmp / "clip_1344.mp4"
        render_text_clip(1344, 64, clip_1344)

        jobs[job_id]["progress"] = "Rendering Media (192)…"
        clip_192 = tmp / "clip_192.mp4"
        src_192 = Path(media_192_path) if media_192_path and Path(media_192_path).exists() else None
        render_text_clip(192, 64, clip_192, src_override=src_192)

        jobs[job_id]["progress"] = "Rendering Longside Left (576)…"
        clip_576_left = tmp / "clip_576_left.mp4"
        render_576_clip(clip_576_left, variant_576_left_path)

        jobs[job_id]["progress"] = "Rendering Longside Right (576)…"
        clip_576_right = tmp / "clip_576_right.mp4"
        render_576_clip(clip_576_right, variant_576_right_path)

        # Copy individual outputs
        out_1728  = OUTPUT_DIR / f"lineup_1728_{job_id[:8]}.mp4"
        out_1344  = OUTPUT_DIR / f"lineup_1344_{job_id[:8]}.mp4"
        out_192   = OUTPUT_DIR / f"lineup_192_{job_id[:8]}.mp4"
        out_576l  = OUTPUT_DIR / f"lineup_576_left_{job_id[:8]}.mp4"
        out_576r  = OUTPUT_DIR / f"lineup_576_right_{job_id[:8]}.mp4"
        shutil.copy(str(clip_1728),      str(out_1728))
        shutil.copy(str(clip_1344),      str(out_1344))
        shutil.copy(str(clip_192),       str(out_192))
        shutil.copy(str(clip_576_left),  str(out_576l))
        shutil.copy(str(clip_576_right), str(out_576r))

        # Build stacked 1920×128 export
        # All clips must be same duration — loop shorter ones to match longest
        jobs[job_id]["progress"] = "Building stacked 1920×128 export…"

        def probe_dur(p):
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                capture_output=True, text=True
            )
            try:
                return float(r.stdout.strip())
            except:
                return total_dur

        def loop_to(src, dst, target_dur):
            d = probe_dur(src)
            if d < target_dur - 0.05:
                run_cmd([
                    "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src),
                    "-t", str(target_dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst),
                ])
                return dst
            return src

        max_dur = max(probe_dur(clip_1728), probe_dur(clip_1344),
                      probe_dur(clip_192), probe_dur(clip_576_left), probe_dur(clip_576_right))

        c1728  = loop_to(clip_1728,      tmp / "l_1728.mp4",       max_dur)
        c1344  = loop_to(clip_1344,      tmp / "l_1344.mp4",       max_dur)
        c192   = loop_to(clip_192,       tmp / "l_192.mp4",        max_dur)
        c576l  = loop_to(clip_576_left,  tmp / "l_576_left.mp4",   max_dur)
        c576r  = loop_to(clip_576_right, tmp / "l_576_right.mp4",  max_dur)

        # Build 1600x1200 stacked export matching AE/ledventure layout
        out_stacked = OUTPUT_DIR / f"lineup_stacked_{job_id[:8]}.mp4"
        build_stacked_export(c1344, c576l, c1728, c576r, c192, out_stacked, fps_val, tmp)

        jobs[job_id]["status"]   = "done"
        jobs[job_id]["progress"] = "Complete!"
        jobs[job_id]["outputs"]  = [
            out_stacked.name,
            out_1728.name,
            out_1344.name,
            out_576l.name,
            out_576r.name,
            out_192.name,
        ]

    except Exception as e:
        jobs[job_id]["status"]   = "error"
        jobs[job_id]["progress"] = str(e)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@app.route("/api/lineup/upload-bg", methods=["POST"])
def lineup_upload_bg():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file"}), 400
    ext = Path(f.filename).suffix.lower()
    if ext not in {".mp4", ".mov", ".avi"}:
        return jsonify({"error": "Background must be a video file"}), 400
    uid  = uuid.uuid4().hex
    dest = UPLOAD_DIR / f"bg_{uid}{ext}"
    f.save(str(dest))
    return jsonify({"ok": True, "path": str(dest), "filename": f.filename})


@app.route("/api/preview/<int:display_id>")
def preview_frame(display_id):
    """Extract first frame from uploaded file and return as JPEG for thumbnail."""
    import tempfile
    slot = request.args.get("slot", "")
    if slot != "":
        # Slot-specific preview
        files = sorted(UPLOAD_DIR.glob(f"*_{display_id}_s{slot}.*"), key=lambda f: f.stat().st_mtime)
        if not files:
            # Fall back to unslotted
            files = sorted(UPLOAD_DIR.glob(f"*_{display_id}.*"), key=lambda f: f.stat().st_mtime)
    else:
        files = sorted(UPLOAD_DIR.glob(f"*_{display_id}.*"), key=lambda f: f.stat().st_mtime)
        # Exclude slot files when no slot specified
        files = [f for f in files if "_s" not in f.stem.split(f"_{display_id}")[1] if len(f.stem.split(f"_{display_id}")) > 1]
        if not files:
            files = sorted(UPLOAD_DIR.glob(f"*_{display_id}.*"), key=lambda f: f.stat().st_mtime)
    if not files:
        abort(404)
    src = files[-1]
    ext = src.suffix.lower()
    tmp = Path(tempfile.mktemp(suffix=".jpg"))
    try:
        if ext in (".png", ".jpg", ".jpeg"):
            run_cmd(["ffmpeg", "-y", "-i", str(src),
                     "-vframes", "1", str(tmp)])
        else:
            # Probe duration, seek to 20% in to avoid black leader frames
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
                capture_output=True, text=True
            )
            try:
                duration = float(probe.stdout.strip())
                seek = duration * 0.2
            except:
                seek = 1.0
            run_cmd(["ffmpeg", "-y", "-ss", str(seek), "-i", str(src),
                     "-vframes", "1", "-q:v", "3", str(tmp)])
        return send_file(str(tmp), mimetype="image/jpeg")
    except:
        abort(500)


@app.route("/api/lineup/select-bg", methods=["POST"])
def lineup_select_bg():
    data     = request.json
    filename = data.get("filename", "")
    path     = BG_DIR / filename
    if not path.exists():
        return jsonify({"error": "File not found"}), 404
    return jsonify({"ok": True, "path": str(path)})


@app.route("/api/lineup/upload-font", methods=["POST"])
def lineup_upload_font():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file"}), 400
    ext = Path(f.filename).suffix.lower()
    if ext not in {".ttf", ".otf"}:
        return jsonify({"error": "Font must be .ttf or .otf"}), 400
    FONT_PATH.parent.mkdir(parents=True, exist_ok=True)
    f.save(str(FONT_PATH))
    return jsonify({"ok": True})


@app.route("/api/lineup/generate", methods=["POST"])
def lineup_generate():
    data      = request.json
    bg_path   = data.get("bg_path")
    number    = str(data.get("number", "")).strip()
    name      = str(data.get("name", "")).strip()
    fps_val   = int(data.get("fps", 30))
    num_dur   = float(data.get("num_dur", 2.0))
    total_dur = float(data.get("total_dur", 6.0))
    fade_dur        = 0.3
    font_name       = data.get("font_name", "")
    variant_576_left  = data.get("variant_576_left", "")
    variant_576_right = data.get("variant_576_right", "")
    variant_576_left_path  = str(VARIANTS_DIR / variant_576_left)  if variant_576_left  and (VARIANTS_DIR / variant_576_left).exists()  else None
    variant_576_right_path = str(VARIANTS_DIR / variant_576_right) if variant_576_right and (VARIANTS_DIR / variant_576_right).exists() else None
    media_192      = data.get("media_192", "")
    media_192_path = str(MEDIA192_DIR / media_192) if media_192 and (MEDIA192_DIR / media_192).exists() else None

    if not bg_path or not Path(bg_path).exists():
        return jsonify({"error": "Background file missing"}), 400
    if not number:
        return jsonify({"error": "Player number required"}), 400
    if not name:
        return jsonify({"error": "Player name required"}), 400

    job_id = uuid.uuid4().hex
    jobs[job_id] = {"status": "queued", "progress": "Queued…", "outputs": []}
    t = threading.Thread(
        target=lineup_worker,
        args=(job_id, Path(bg_path), variant_576_left_path, variant_576_right_path, media_192_path, number, name, fps_val, fade_dur, num_dur, total_dur, font_name),
        daemon=True,
    )
    t.start()
    return jsonify({"job_id": job_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
