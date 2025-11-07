import logging
from pathlib import Path
from typing import Optional
from tqdm import tqdm
from .scanner import scan_input_files
from .date_extractor import extract_dates
from .mover import get_unique_filename, safe_move, backup_file


def remove_empty_dirs(path: Path):
    dirs = [d for d in path.rglob('*') if d.is_dir()]
    dirs.sort(key=lambda d: len(d.parts), reverse=True)
    for d in dirs:
        try:
            if not any(d.iterdir()):
                d.rmdir()
                logging.info(f'Removed empty folder: {d}')
        except Exception as e:
            logging.warning(f'Failed to remove folder {d}: {e}')


def organize_files(
    input_dir: str,
    output_dir: str,
    backup_dir: Optional[str] = None,
    create_backup: bool = False,
    clean_empty_input: bool = False,
    dry_run: bool = False,
):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    img_path = output_path / 'IMG'
    rnd_path = output_path / 'RND'

    if not dry_run:
        img_path.mkdir(parents=True, exist_ok=True)
        rnd_path.mkdir(parents=True, exist_ok=True)

    supported, skipped = scan_input_files(input_path)
    if skipped:
        print(f'Warning: Skipped {len(skipped)} files (unsupported extension). See log for details.')
        for f in skipped:
            logging.warning(f'Skipped {f} due to unsupported extension.')

    file_dates = extract_dates(supported)
    sorted_files = sorted(file_dates, key=lambda x: x[1])

    i = 0
    j = 0

    for f, dt, source in tqdm(sorted_files, desc='Moving files'):
        suffix = f.suffix.lower()

        if source == 'EXIF':
            prefix = 'IMG'
            dest_folder = img_path
            filename = f'{prefix}_{i:04d}{suffix}'
            i += 1
        else:
            prefix = 'RND'
            dest_folder = rnd_path
            filename = f'{prefix}_{j:04d}{suffix}'
            j += 1

        destination = get_unique_filename(dest_folder / filename)

        if create_backup and backup_dir:
            try:
                if dry_run:
                    logging.info(f'[DRY RUN] Would backup {f} to {backup_dir}')
                else:
                    backup_file(f, Path(backup_dir))
                    logging.info(f'Backed up {f} to {backup_dir}')
            except Exception as e:
                logging.warning(f'Backup failed for {f}: {e}')

        if dry_run:
            logging.info(f'[DRY RUN] Would move {f} → {destination}')
            continue

        try:
            safe_move(f, destination)
            logging.info(f'Moved: {f} → {destination} (source={source})')
        except Exception as e:
            logging.error(f'Failed to move {f} → {destination}, skipping: {e}')

    if clean_empty_input and (not dry_run):
        try:
            remove_empty_dirs(input_path)
        except Exception as e:
            logging.warning(f'Failed to remove empty input directories: {e}')

    print('Done organizing files.')
    total = len(sorted_files)
    print(f'Total processed: {total}, EXIF count: {i}, fallback count: {j}')
    if create_backup and backup_dir:
        print(f'Backups stored in: {backup_dir}')
    if skipped:
        print(f'{len(skipped)} files were skipped (unsupported extension).')

    return None
