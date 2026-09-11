import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingest import IMAGE_EXTENSIONS, compute_file_hash, scan_photo_dir


def test_scan_photo_dir_filters_by_extension(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"fake")
    (tmp_path / "b.txt").write_text("not an image")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.png").write_bytes(b"fake")

    found = {p.name for p in scan_photo_dir(tmp_path)}

    assert found == {"a.jpg", "c.png"}
    assert ".jpg" in IMAGE_EXTENSIONS


def test_compute_file_hash_is_stable(tmp_path):
    f = tmp_path / "a.jpg"
    f.write_bytes(b"same content")

    assert compute_file_hash(f) == compute_file_hash(f)
