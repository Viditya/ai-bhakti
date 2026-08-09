"""Portable discovery for external production tools.

Project-local tools under .tools/ take precedence over PATH.  This keeps the
video pipeline reproducible on a fresh Windows machine without modifying the
user's system-wide PATH.
"""

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_binary(name: str) -> str:
    """Return an executable path for *name*, preferring the local toolchain."""
    suffixes = (f"{name}.exe", name)
    for suffix in suffixes:
        for candidate in (PROJECT_ROOT / ".tools" / "ffmpeg").rglob(suffix):
            if candidate.is_file():
                return str(candidate)

    discovered = shutil.which(name)
    if discovered:
        return discovered
    raise FileNotFoundError(
        f"{name} was not found. Install the portable FFmpeg runtime under "
        f"{PROJECT_ROOT / '.tools' / 'ffmpeg'} or add it to PATH."
    )
