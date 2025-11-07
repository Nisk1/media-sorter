import argparse
import logging
import os
from datetime import datetime
from .organizer import organize_files
from .utils import setup_logging

def main():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_log_file = os.path.join(log_dir, f"log_file-{timestamp}.txt")

    parser = argparse.ArgumentParser(description="Media file sorter by date")
    parser.add_argument("input_dir", help="Input directory to scan")
    parser.add_argument("output_dir", help="Output directory to place sorted files")
    parser.add_argument("--backup-dir", help="Directory to store backups", default=None)
    parser.add_argument("--no-backup", action="store_true", help="Do not create backups")
    parser.add_argument("--clean-empty", action="store_true", help="Remove empty input dirs after move")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without moving files")
    parser.add_argument("--log-file", help="Path to log file", default=default_log_file)
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose console output (INFO level)"
    )
    
    args = parser.parse_args()
    
    console_level = logging.INFO if args.verbose else logging.CRITICAL + 10

    setup_logging(args.log_file, console_level=console_level)

    if not args.no_backup and args.backup_dir is None:
        parser.error("--backup-dir is required unless --no-backup is specified")

    create_backup = not args.no_backup

    print("Starting Media Sorter")
    if args.dry_run:
        print("Dry run mode: no files will be moved or backed up.")
    if create_backup:
        print(f"Backups will be stored in: {args.backup_dir}")

    organize_files(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        backup_dir=args.backup_dir,
        create_backup=create_backup,
        clean_empty_input=args.clean_empty,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
