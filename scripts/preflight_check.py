"""
preflight_check.py — one command to check whether this pipeline can
actually run right now, instead of discovering blockers one at a time
mid-run. Run this after setting credentials / adding a character lock:
  python scripts/preflight_check.py

Checks nothing it can't verify honestly — e.g. it confirms credentials
are SET, not that they're valid (that requires a real API call, which
costs money and belongs to the first real run, not a free preflight).
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check(label: str, ok: bool, detail: str = "") -> bool:
    status = "OK" if ok else "MISSING"
    line = f"[{status}] {label}"
    if detail:
        line += f" - {detail}"
    print(line)
    return ok


def main() -> int:
    results = []

    # Credentials — presence only, not validity.
    import os
    for env_var in (
        "HIGGSFIELD_API_KEY",
        "HIGGSFIELD_API_KEY_SECRET",
        "HIGGSFIELD_SOUL_ID",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
    ):
        results.append(check(f"env var {env_var}", bool(os.environ.get(env_var))))

    # Character lock required by the active batch, not merely any PNG.
    lock_dir = PROJECT_ROOT / "references" / "character_locks"
    active_lock = lock_dir / "hanuman_v1.png"
    results.append(check(
        "references/character_locks/hanuman_v1.png",
        active_lock.is_file(),
        "approved active-batch character reference",
    ))

    watermark = PROJECT_ROOT / "references" / "brand" / "watermark.png"
    results.append(check(
        "references/brand/watermark.png",
        watermark.is_file(),
        "required by the brand specification",
    ))

    # System binaries required by scripts/ffmpeg_assemble.py.
    for binary in ("ffmpeg", "ffprobe"):
        results.append(check(f"{binary} on PATH", shutil.which(binary) is not None))

    # Python deps.
    for module in ("requests", "PIL"):
        try:
            __import__(module)
            results.append(check(f"python module {module}", True))
        except ImportError:
            results.append(check(f"python module {module}", False, "pip install -r requirements.txt"))

    # face_recognition is optional (heavy dlib build) — warn, don't fail.
    try:
        __import__("face_recognition")
        check("python module face_recognition (optional)", True)
    except ImportError:
        check("python module face_recognition (optional)", False, "Mode B falls back to manual scoring without it")

    print()
    if all(results):
        print("READY: all required checks passed. Safe to run Chitrkar/Sangeet for real.")
        return 0
    else:
        print("NOT READY: fix the MISSING items above before running production steps.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
