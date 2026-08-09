"""
preflight_check.py — one command to check whether this pipeline can
actually run right now, instead of discovering blockers one at a time
mid-run. Run this after setting credentials / adding a character lock:
  python scripts/preflight_check.py

Checks nothing it can't verify honestly — e.g. it confirms credentials
are SET, not that they're valid (that requires a real API call, which
costs money and belongs to the first real run, not a free preflight).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
from toolchain import find_binary


def check(label: str, ok: bool, detail: str = "") -> bool:
    status = "OK" if ok else "MISSING"
    line = f"[{status}] {label}"
    if detail:
        line += f" - {detail}"
    print(line)
    return ok


def warn(label: str, detail: str = "") -> None:
    line = f"[OPTIONAL] {label}"
    if detail:
        line += f" - {detail}"
    print(line)


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

    # The active pilot selects its lock through the versioned registry.
    active_lock = PROJECT_ROOT / "references" / "character_locks" / "hanuman" / "mature_adult" / "reference_v1.png"
    results.append(check(
        "active Hanuman character lock",
        active_lock.is_file(),
        "approved active-batch character reference",
    ))

    watermark = PROJECT_ROOT / "references" / "brand" / "watermark.png"
    results.append(check(
        "references/brand/watermark.png",
        watermark.is_file(),
        "required by the brand specification",
    ))

    # Project-local portable binaries are preferred; PATH remains supported.
    for binary in ("ffmpeg", "ffprobe"):
        try:
            binary_path = find_binary(binary)
            results.append(check(f"{binary} available", True, binary_path))
        except FileNotFoundError:
            results.append(check(f"{binary} available", False, "install the portable toolchain or add it to PATH"))

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
        warn("python module face_recognition", "automated Mode B scoring available")
    except ImportError:
        warn("python module face_recognition", "manual visual identity review is required instead")

    print()
    if all(results):
        print("READY: all required checks passed. Safe to run Chitrkar/Sangeet for real.")
        return 0
    else:
        print("NOT READY: fix the MISSING items above before running production steps.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
