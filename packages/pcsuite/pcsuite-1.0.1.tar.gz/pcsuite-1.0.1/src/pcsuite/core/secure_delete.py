import os
import random
from pathlib import Path

def secure_delete(path: Path, passes: int = 3):
    """Overwrite file with random data before deleting (multi-pass wipe)."""
    if not path.is_file():
        return False
    length = path.stat().st_size
    try:
        with open(path, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(length))
                f.flush()
        path.unlink()
        return True
    except Exception:
        return False
