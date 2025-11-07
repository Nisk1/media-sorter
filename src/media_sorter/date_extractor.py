import logging
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
from pymediainfo import MediaInfo
from dateutil.parser import isoparse

register_heif_opener()

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
VIDEO_EXTS = {'.mov', '.mp4', '.avi', '.mkv'}

MEDIA_DATE_ATTRS = [
    'comapplequicktimecreationdate',
    'creation_time',
    'encoded_date',
    'tagged_date',
    'file_creation_date',
    'file_modification_date',
]


def _extract_exif_date(path: Path) -> Optional[datetime]:
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return None
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag in ('DateTimeOriginal', 'DateTime'):
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except Exception:
                            pass
                    if not isinstance(value, str):
                        continue
                    for fmt in ('%Y:%m:%d %H:%M:%S', '%Y:%m:%d %H:%M', '%Y-%m-%d %H:%M:%S'):
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    logging.warning(f"Unsupported EXIF datetime format `{value}` in {path}")
                    return None
    except UnidentifiedImageError:
        return None
    except Exception as e:
        logging.warning(f"Error opening image {path}: {e}")
        return None
    return None


def _extract_media_metadata_date(path: Path) -> Optional[datetime]:
    try:
        media = MediaInfo.parse(path)
    except Exception as e:
        logging.warning(f"MediaInfo.parse error for {path}: {e}")
        return None

    for track in media.tracks:
        if track.track_type == "General":
            data = track.to_data()
            for attr in MEDIA_DATE_ATTRS:
                val = data.get(attr)
                if val:
                    try:
                        dt = isoparse(val)
                        return dt
                    except Exception as e:
                        logging.warning(f"Cannot parse `{val}` for {attr} in {path}: {e}")
                        continue
    return None


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(timezone.utc)


def extract_dates(files: List[Path]) -> List[Tuple[Path, datetime, str]]:
    res = []
    for f in files:
        dt = None
        src = None
        ext = f.suffix.lower()
        if ext in IMAGE_EXTS:
            dt0 = _extract_exif_date(f)
            if dt0:
                dt = _to_utc(dt0)
                src = 'EXIF'
            else:
                dt1 = _extract_media_metadata_date(f)
                if dt1:
                    dt = _to_utc(dt1)
                    src = 'MEDIA'
        elif ext in VIDEO_EXTS:
            dt1 = _extract_media_metadata_date(f)
            if dt1:
                dt = _to_utc(dt1)
                src = 'MEDIA'

        if dt is None:
            try:
                ts = f.stat().st_mtime
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                src = 'OS'
            except Exception as e:
                logging.warning(f"Cannot stat file {f}: {e}")
                continue

        res.append((f, dt, src))
    return res
