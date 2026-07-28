"""
youtube_upload.py — upload gate with a REAL enforced check, not just a
prose instruction telling agents not to call it.

This script will REFUSE to run unless the video's PROGRESS.md entry has
`human_approved: true`. This is the actual safety mechanism VISION.md and
CLAUDE.md describe — code enforcement backing up the instruction, since
instructions alone can be missed or overridden by a confident agent.

The actual YouTube Data API upload call itself is NOT implemented here —
confirm current YouTube Data API v3 quota/auth requirements (OAuth consent
screen, quota increase request for regular uploads) before implementing
that part. This stub's job is to demonstrate and enforce the approval
gate correctly; wire in the real upload call only after that's solid.
"""

import re
import sys
from pathlib import Path


class ApprovalNotGrantedError(Exception):
    pass


def _read_progress_entry(progress_md_path: str, video_id: str) -> str:
    content = Path(progress_md_path).read_text(encoding="utf-8")
    # crude but effective: find the block starting at "## <video_id>"
    # up to the next "## " heading or end of file
    pattern = rf"## {re.escape(video_id)}\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise ValueError(f"No PROGRESS.md entry found for {video_id}")
    return match.group(1)


def is_approved(progress_md_path: str, video_id: str) -> bool:
    entry = _read_progress_entry(progress_md_path, video_id)
    # look for "human_approved: true" specifically, not just "true"
    # anywhere in the block
    match = re.search(r"human_approved:\s*(true|false)", entry, re.IGNORECASE)
    if not match:
        return False
    return match.group(1).lower() == "true"


def upload(
    video_id: str,
    final_video_path: str,
    progress_md_path: str = "PROGRESS.md",
    confirmed: bool = False,
) -> dict:
    """
    Refuses to proceed unless:
    1. `confirmed=True` is explicitly passed (a human/orchestrator has to
       deliberately set this — it's not the default), AND
    2. PROGRESS.md for this video_id has human_approved: true.

    Both checks exist because relying on either alone (a flag OR a file
    value) is one point of failure away from an accidental upload.
    """
    if not confirmed:
        raise ApprovalNotGrantedError(
            f"upload() called without confirmed=True for {video_id}. "
            "This is not a bug to work around — it means the caller "
            "hasn't deliberately authorized this upload."
        )
    if not is_approved(progress_md_path, video_id):
        raise ApprovalNotGrantedError(
            f"PROGRESS.md does not show human_approved: true for "
            f"{video_id}. Refusing to upload. Set it explicitly after "
            f"human review, then retry."
        )
    if not Path(final_video_path).is_file():
        raise FileNotFoundError(f"Final video does not exist: {final_video_path}")

    # TODO: real YouTube Data API v3 upload call goes here.
    # Confirm current OAuth flow and quota requirements before
    # implementing — regular API quota may require a Google quota
    # increase request for anything beyond a handful of uploads/day.
    raise NotImplementedError(
        "Approval gate passed. Actual YouTube Data API upload call is "
        "not yet implemented — confirm current API requirements first."
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python youtube_upload.py <video_id> <final_video_path> [--confirmed]")
        sys.exit(1)
    video_id, final_video_path = sys.argv[1], sys.argv[2]
    confirmed = "--confirmed" in sys.argv
    try:
        result = upload(video_id, final_video_path, confirmed=confirmed)
        print(result)
    except (ApprovalNotGrantedError, NotImplementedError) as e:
        print(f"BLOCKED: {e}")
        sys.exit(1)
