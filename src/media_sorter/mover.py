import logging
from pathlib import Path
import shutil

def get_unique_filename(destination: Path) -> Path:
    counter = 1
    original = destination
    while destination.exists():
        destination = original.with_name(f"{original.stem}_{counter}{original.suffix}")
        counter += 1
    return destination


def safe_move(src: Path, dst: Path):
    try:
        src.replace(dst)
    except Exception:
        try:
            shutil.move(str(src), str(dst))
        except Exception as e:
            logging.error(f"Failed to move {src} to {dst}: {e}")
            raise


def backup_file(src: Path, backup_folder: Path) -> bool:
    try:
        backup_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create backup folder {backup_folder}: {e}")
        return False

    backup_path = backup_folder / src.name
    backup_path = get_unique_filename(backup_path)
    try:
        shutil.copy2(src, backup_path)
        return True
    except Exception as e:
        logging.error(f"Backup failed for {src} → {backup_path}: {e}")
        return False
