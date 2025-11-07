import logging
from pathlib import Path
from typing import List, Tuple

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
VIDEO_EXTS = {'.mov', '.mp4', '.avi', '.mkv'}
VALID_EXTS = IMAGE_EXTS.union(VIDEO_EXTS)


def scan_input_files(input_dir: Path) -> Tuple[List[Path], List[Path]]:
    supported = []
    skipped = []
    for f in input_dir.rglob('*'):
        try:
            if not f.is_file() or f.is_symlink():
                continue
        except OSError as e:
            logging.warning(f"Cannot inspect path {f}: {e}")
            continue

        ext = f.suffix.lower()
        if ext in VALID_EXTS:
            supported.append(f)
        else:
            skipped.append(f)

    return supported, skipped
