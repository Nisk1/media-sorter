import logging

def setup_logging(log_path: str, console_level=logging.CRITICAL + 10):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    if root.hasHandlers():
        root.handlers.clear()

    fh = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    root.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root.addHandler(ch)
