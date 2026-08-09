"""
Generates a small synthetic test clip (color video + tone audio + a fake
watermark box) and runs the real verification functions from
scripts/ffmpeg_assemble.py against it, to prove they actually work —
not just that they look plausible on paper.

Run: python3 tests/test_ffmpeg_assemble.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import ffmpeg_assemble as fa  # noqa: E402
from toolchain import find_binary  # noqa: E402

TMP = Path(tempfile.gettempdir()) / "ai_bhakti_test_assets"
TMP.mkdir(exist_ok=True)


def make_good_clip():
    """5s, 1080x1920, gold-ish color, tone audio matching duration, with a
    visible box drawn in the watermark region."""
    video_path = str(TMP / "good_video.mp4")
    audio_path = str(TMP / "good_audio.wav")

    # 5 seconds of a warm-gold color video with a white box bottom-right
    # (simulating a watermark) drawn via drawbox filter.
    subprocess.run([
        find_binary("ffmpeg"), "-y", "-f", "lavfi",
        "-i", "color=c=0x8a6a1e:s=1080x1920:d=5",
        "-vf", "drawbox=x=810:y=1650:w=220:h=220:color=white:t=fill",
        video_path,
    ], check=True, capture_output=True)

    # 5 seconds of a 440Hz tone as narration stand-in
    subprocess.run([
        find_binary("ffmpeg"), "-y", "-f", "lavfi",
        "-i", "sine=frequency=440:duration=5",
        audio_path,
    ], check=True, capture_output=True)

    return video_path, audio_path


def make_bad_clip():
    """3s black video (should fail blank-frame + watermark checks),
    5s audio (should fail duration match)."""
    video_path = str(TMP / "bad_video.mp4")
    audio_path = str(TMP / "bad_audio.wav")

    subprocess.run([
        find_binary("ffmpeg"), "-y", "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:d=3",
        video_path,
    ], check=True, capture_output=True)

    subprocess.run([
        find_binary("ffmpeg"), "-y", "-f", "lavfi",
        "-i", "sine=frequency=440:duration=5",
        audio_path,
    ], check=True, capture_output=True)

    return video_path, audio_path


def run():
    print("=== Testing GOOD clip (should pass all checks) ===")
    good_video, good_audio = make_good_clip()
    good_result = fa.verify_all(good_video, good_audio)
    print(good_result)
    assert good_result["duration_match"] is True, "expected duration match on good clip"
    assert good_result["resolution_ok"] is True, "expected resolution ok on good clip"
    assert good_result["no_blank_frames"] is True, "expected no blank frames on good clip"
    assert good_result["watermark_present"] is True, "expected watermark detected on good clip"
    print("PASS: all four checks correctly returned True on the good clip.\n")

    print("=== Testing BAD clip (should fail duration/blank/watermark checks) ===")
    bad_video, bad_audio = make_bad_clip()
    bad_result = fa.verify_all(bad_video, bad_audio)
    print(bad_result)
    assert bad_result["duration_match"] is False, "expected duration MISMATCH on bad clip"
    assert bad_result["no_blank_frames"] is False, "expected BLANK frames detected on bad clip"
    assert bad_result["watermark_present"] is False, "expected NO watermark on bad clip"
    print("PASS: all three failure checks correctly returned False on the bad clip.\n")

    print("ALL TESTS PASSED — verification functions are real and working.")


if __name__ == "__main__":
    run()
