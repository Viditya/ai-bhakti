"""Command-line entry point for supervised Short assembly."""

import argparse
import json

from ffmpeg_assemble import assemble_video, verify_all


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot", action="append", required=True)
    parser.add_argument("--narration", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bgm")
    parser.add_argument("--watermark")
    parser.add_argument("--captions")
    args = parser.parse_args()

    final_path = assemble_video(
        args.shot,
        args.narration,
        args.output,
        bgm_audio_path=args.bgm,
        watermark_path=args.watermark,
        captions_srt_path=args.captions,
    )
    verification = verify_all(final_path, args.narration)
    print(json.dumps({"final_video_path": final_path, "verification": verification}, indent=2))
    return 0 if all(verification.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
