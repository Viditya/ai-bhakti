"""
consistency_check.py — automated face-similarity scoring for Parakh's
Mode B gate (shot-to-shot character consistency), so this stops requiring
a human to eyeball every shot — that doesn't scale to 1 video/day.

Uses the `face_recognition` library (dlib-based), the standard lightweight
choice for this. NOT pre-installed by requirements.txt because it needs
dlib, which needs a C++ build toolchain (cmake + Visual Studio Build Tools
on Windows) — a much heavier install than this project's other deps.
Install before using this script:
  pip install face_recognition
If that fails on Windows, install "Desktop development with C++" via the
Visual Studio Build Tools installer first, then retry.

Scoring: face_recognition.face_distance returns 0.0 (identical) to ~1.0+
(different); 0.6 is its own commonly-cited match/no-match threshold. We
convert to a 0-1 similarity score via `1 - distance` (clamped to [0, 1])
so it's directly comparable to Parakh's documented min_score >= 0.55 gate.
"""

from pathlib import Path
from typing import List

import face_recognition


class NoFaceFoundError(Exception):
    pass


def _encoding(image_path: str):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise NoFaceFoundError(f"No face detected in {image_path}")
    return encodings[0]


def score_shot(reference_encoding, shot_image_path: str) -> float:
    """Returns a 0-1 similarity score for one shot against the reference."""
    shot_encoding = _encoding(shot_image_path)
    distance = face_recognition.face_distance([reference_encoding], shot_encoding)[0]
    return max(0.0, min(1.0, 1.0 - distance))


def check_consistency(reference_image_path: str, shot_image_paths: List[str]) -> dict:
    """
    Matches Parakh Mode B's exact output contract (see
    .claude/skills/parakh/SKILL.md) so the orchestrator can call this
    directly instead of asking Parakh to guess at a number.

    Returns:
    {
      "consistency_scores": [0.0, ...],
      "min_score": 0.0,
      "pass": bool,   # True only if min_score >= 0.55
      "flagged_shots": [paths below 0.55]
    }
    """
    reference_encoding = _encoding(reference_image_path)
    scores = []
    flagged = []
    for shot_path in shot_image_paths:
        score = score_shot(reference_encoding, shot_path)
        scores.append(score)
        if score < 0.55:
            flagged.append(shot_path)

    min_score = min(scores) if scores else 0.0
    return {
        "consistency_scores": scores,
        "min_score": min_score,
        "pass": min_score >= 0.55,
        "flagged_shots": flagged,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 3:
        print("Usage: python consistency_check.py <reference_image_path> <shot1> [shot2 ...]")
        sys.exit(1)
    result = check_consistency(sys.argv[1], sys.argv[2:])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["pass"] else 1)
