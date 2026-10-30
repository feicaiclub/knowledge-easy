#!/usr/bin/env python3
"""Register immutable review revisions. No film changes, no framework dependency."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile


def read_json(path, default=None):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else default


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".writing-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inside(root, relative):
    path = (Path(root) / relative).resolve()
    path.relative_to(Path(root).resolve())
    if not path.is_file():
        raise ValueError(f"File not found: {relative}")
    return path


def probe(path):
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ]))
    stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = map(int, stream["avg_frame_rate"].split("/"))
    duration = float(stream.get("duration", info["format"]["duration"]))
    # Frame review targets CFR delivery files. VFR needs an explicit PTS index.
    if stream["r_frame_rate"] != stream["avg_frame_rate"]:
        raise ValueError("Frame review requires a constant-frame-rate file. Export a CFR review copy first.")
    frames = int(stream.get("nb_frames", round(duration * num / den)))
    return {"fps_num": num, "fps_den": den, "duration": duration,
            "frames": frames, "width": stream["width"], "height": stream["height"]}


def register(root, path, label, revision_id, audio=None, timeline=None, review=None):
    root = Path(root).resolve()
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", revision_id):
        raise ValueError("Revision IDs may contain letters, numbers, underscores, and hyphens only.")
    file = inside(root, path)
    manifest_path = root / "review/studio.json"
    manifest = read_json(manifest_path, {"schema_version": 1, "title": root.name, "revisions": []})
    existing = next((r for r in manifest["revisions"] if r["id"] == revision_id), None)
    revision = {"id": revision_id, "label": label, "path": str(file.relative_to(root)),
                "sha256": digest(file), **probe(file), "chapters": [], "objects": []}
    if audio:
        source = inside(root, audio)
        revision["audio_override"] = str(source.relative_to(root))
        revision["audio_sha256"] = digest(source)
    if timeline:
        data = read_json(inside(root, timeline))
        revision["chapters"] = data.get("chapters", [])
        revision["objects"] = data.get("objects", [])
    review_spec = None
    if review:
        notes = inside(root, review)
        if notes.suffix.lower() not in (".md", ".txt") or notes.stat().st_size > 256 * 1024:
            raise ValueError("Review notes must be a Markdown or text file no larger than 256 KiB.")
        review_spec = {"path": str(notes.relative_to(root)), "title": label + " · Review"}
    if existing:
        if existing != revision:
            raise ValueError("This revision ID already refers to different content. Use a new ID to preserve feedback locations.")
        if review_spec is not None:
            manifest.setdefault("self_reviews", {})[revision_id] = review_spec
            atomic_json(manifest_path, manifest)
        return revision
    # Bind legacy notes to the version they belonged to before changing the current version.
    previous_id = manifest.get("current_revision")
    legacy_review = manifest.pop("self_review", None)
    if legacy_review and previous_id:
        manifest.setdefault("self_reviews", {}).setdefault(previous_id, legacy_review)
    manifest["revisions"].append(revision)
    manifest["current_revision"] = revision_id
    if review_spec is not None:
        manifest.setdefault("self_reviews", {})[revision_id] = review_spec
    elif legacy_review and not previous_id:
        manifest.setdefault("self_reviews", {})[revision_id] = legacy_review
    atomic_json(manifest_path, manifest)
    return revision



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--file")
    ap.add_argument("--label")
    ap.add_argument("--id")
    ap.add_argument("--audio")
    ap.add_argument("--timeline")
    ap.add_argument("--review-file", help="Review notes for this revision, relative to the project.")
    args = ap.parse_args()
    if not (args.file and args.label and args.id):
        ap.error("Registering a revision requires --file, --label, and --id.")
    register(args.project, args.file, args.label, args.id, args.audio, args.timeline, args.review_file)
    print(str(Path(args.project).resolve() / "review/studio.json"))
