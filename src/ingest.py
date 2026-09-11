"""Scan a photo folder and incrementally embed new/changed images."""
import hashlib
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def scan_photo_dir(photo_dir):
    photo_dir = Path(photo_dir)
    return [p for p in photo_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS]


def compute_file_hash(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def extract_taken_at(path):
    try:
        img = Image.open(path)
        exif = img._getexif() if hasattr(img, "_getexif") else None
        if not exif:
            return None
        for tag_id, value in exif.items():
            if TAGS.get(tag_id) == "DateTimeOriginal":
                return str(value)
    except Exception:
        return None
    return None


def find_new_or_changed(photo_dir, metadata_store):
    """Files whose mtime differs from what's stored (or aren't indexed yet)."""
    changed = []
    for path in scan_photo_dir(photo_dir):
        mtime = path.stat().st_mtime
        existing = metadata_store.get_by_path(str(path))
        if existing and existing[2] == mtime:
            continue
        changed.append(path)
    return changed


def run_ingest(config, metadata_store, index_store, embedder, progress_callback=None):
    targets = find_new_or_changed(config["photo_dir"], metadata_store)
    total = len(targets)

    for i, path in enumerate(targets):
        try:
            with Image.open(path) as img:
                width, height = img.size
        except Exception:
            continue

        file_hash = compute_file_hash(path)
        mtime = path.stat().st_mtime
        taken_at = extract_taken_at(path)
        photo_id = metadata_store.upsert(str(path), file_hash, mtime, width, height, taken_at)

        vector = embedder.encode_image(path)
        index_store.add([photo_id], [vector])

        if progress_callback:
            progress_callback(i + 1, total, path)

    index_store.save()
    return total
