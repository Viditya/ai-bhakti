"""
ffmpeg_assemble.py — REAL, TESTED verification functions for Sampadak.

These are not aspirational stubs — see tests/test_ffmpeg_assemble.py for
a working end-to-end test run against a generated sample clip.

Requires: ffmpeg and ffprobe on PATH (system binaries, not a pip package).
Optional: Pillow (for watermark region check).

USAGE NOTE FOR THE ORCHESTRATOR / SAMPADAK SKILL:
Call verify_all() after assembly. Do not report a video as done unless
every field in its return dict is True.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image


def _ffprobe_duration(media_path: str) -> float:
    """Return duration in seconds for any audio/video file, via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", media_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def check_duration_match(
    audio_path: str, video_path: str, tolerance_sec: float = 0.5
) -> bool:
    """True if |audio_duration - video_duration| < tolerance_sec."""
    audio_dur = _ffprobe_duration(audio_path)
    video_dur = _ffprobe_duration(video_path)
    return abs(audio_dur - video_dur) < tolerance_sec


def check_resolution(video_path: str, expected=(1080, 1920)) -> bool:
    """True if video resolution matches expected (width, height)."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json", video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stream = json.loads(result.stdout)["streams"][0]
    return (stream["width"], stream["height"]) == expected


def _extract_frame(video_path: str, timestamp_sec: float, out_path: str) -> bool:
    """Extract a single frame at timestamp_sec. Returns True on success."""
    cmd = [
        "ffmpeg", "-y", "-ss", str(timestamp_sec), "-i", video_path,
        "-frames:v", "1", out_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0 and Path(out_path).exists()


def check_no_blank_frames(
    video_path: str, sample_count: int = 5, brightness_threshold: float = 5.0
) -> bool:
    """
    Samples `sample_count` frames evenly across the video and checks none
    are near-black (mean pixel brightness below brightness_threshold on a
    0-255 grayscale scale). Returns True if all sampled frames pass.
    """
    duration = _ffprobe_duration(video_path)
    tmp_dir = Path(tempfile.gettempdir()) / "ai_bhakti_frame_check"
    tmp_dir.mkdir(exist_ok=True)

    for i in range(sample_count):
        # avoid exact 0.0 / exact end, sample interior points
        t = duration * (i + 1) / (sample_count + 1)
        frame_path = str(tmp_dir / f"frame_{i}.png")
        if not _extract_frame(video_path, t, frame_path):
            return False
        img = Image.open(frame_path).convert("L")
        mean_brightness = sum(img.getdata()) / (img.width * img.height)
        if mean_brightness < brightness_threshold:
            return False
    return True


def check_watermark_present(
    video_path: str,
    watermark_region: tuple = (0.75, 0.85, 1.0, 1.0),
    sample_count: int = 3,
    min_variance: float = 5.0,
) -> bool:
    """
    Heuristic watermark check: samples frames and checks the watermark
    region (default: bottom-right 25% width x 15% height, as fractions of
    frame size) has non-trivial pixel variance — i.e. something is drawn
    there, not empty background.

    NOTE: this is a presence heuristic, not content verification. It
    confirms *something* is rendered in the watermark region consistently
    across sampled frames — it does not confirm it's the CORRECT logo.
    For real deployments, consider template-matching against your actual
    watermark asset if false positives matter.
    """
    duration = _ffprobe_duration(video_path)
    tmp_dir = Path(tempfile.gettempdir()) / "ai_bhakti_frame_check"
    tmp_dir.mkdir(exist_ok=True)

    for i in range(sample_count):
        t = duration * (i + 1) / (sample_count + 1)
        frame_path = str(tmp_dir / f"wm_frame_{i}.png")
        if not _extract_frame(video_path, t, frame_path):
            return False
        img = Image.open(frame_path).convert("L")
        w, h = img.size
        left, top, right, bottom = (
            int(watermark_region[0] * w), int(watermark_region[1] * h),
            int(watermark_region[2] * w), int(watermark_region[3] * h),
        )
        region = img.crop((left, top, right, bottom))
        pixels = list(region.getdata())
        mean = sum(pixels) / len(pixels)
        variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
        if variance < min_variance:
            return False
    return True


def verify_all(
    video_path: str,
    audio_path: str,
    expected_resolution=(1080, 1920),
) -> dict:
    """
    Runs all four checks and returns the verification dict expected by
    the sampadak SKILL.md output schema. Call this — don't hand-roll
    equivalent logic inline.
    """
    return {
        "duration_match": check_duration_match(audio_path, video_path),
        "watermark_present": check_watermark_present(video_path),
        "no_blank_frames": check_no_blank_frames(video_path),
        "resolution_ok": check_resolution(video_path, expected_resolution),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python ffmpeg_assemble.py <video_path> <audio_path>")
        sys.exit(1)
    result = verify_all(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
    sys.exit(0 if all(result.values()) else 1)
