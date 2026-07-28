import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import ffmpeg_assemble as fa  # noqa: E402
import captions  # noqa: E402
import higgsfield_client as hf  # noqa: E402
import youtube_upload as yu  # noqa: E402


class ApprovalGateTests(unittest.TestCase):
    def test_utf8_progress_is_parsed_on_windows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            progress = Path(temp_dir) / "PROGRESS.md"
            progress.write_text(
                "# प्रगति\n\n## video_001\n- human_approved: true\n",
                encoding="utf-8",
            )
            self.assertTrue(yu.is_approved(str(progress), "video_001"))

    def test_upload_requires_existing_final_video(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            progress = Path(temp_dir) / "PROGRESS.md"
            progress.write_text(
                "## video_001\n- human_approved: true\n",
                encoding="utf-8",
            )
            with self.assertRaises(FileNotFoundError):
                yu.upload(
                    "video_001",
                    str(Path(temp_dir) / "missing.mp4"),
                    str(progress),
                    confirmed=True,
                )


class AssemblyTests(unittest.TestCase):
    def test_assembly_builds_ffmpeg_command_without_spending(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shots = [root / "shot1.png", root / "shot2.png"]
            narration = root / "narration.mp3"
            bgm = root / "bgm.mp3"
            watermark = root / "watermark.png"
            captions = root / "captions.srt"
            for path in [*shots, narration, bgm, watermark, captions]:
                path.write_bytes(b"test")
            output = root / "final" / "video.mp4"

            with (
                patch.object(fa, "_ffprobe_duration", return_value=10.0),
                patch.object(fa.subprocess, "run") as run,
            ):
                result = fa.assemble_video(
                    [str(path) for path in shots],
                    str(narration),
                    str(output),
                    bgm_audio_path=str(bgm),
                    watermark_path=str(watermark),
                    captions_srt_path=str(captions),
                )

            self.assertEqual(result, str(output))
            command = run.call_args.args[0]
            filter_graph = command[command.index("-filter_complex") + 1]
            self.assertIn("concat=n=2", filter_graph)
            self.assertIn("overlay=", filter_graph)
            self.assertIn("subtitles=", filter_graph)
            self.assertIn("amix=inputs=2", filter_graph)
            self.assertTrue(output.parent.is_dir())

    def test_assembly_rejects_empty_shot_list(self):
        with self.assertRaises(ValueError):
            fa.assemble_video([], "narration.mp3", "video.mp4")

    def test_caption_fallback_writes_utf8_srt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "captions.srt"
            captions.write_even_srt(
                "हनुमान जी ने सूर्य को फल समझा",
                10,
                str(output),
                max_chars=12,
            )
            content = output.read_text(encoding="utf-8")
            self.assertIn("00:00:00,000 -->", content)
            self.assertIn("हनुमान", content)


class ProviderBoundaryTests(unittest.TestCase):
    def test_higgsfield_asset_url_known_response(self):
        self.assertEqual(
            hf._asset_url({"images": [{"url": "https://example.test/shot.png"}]}),
            "https://example.test/shot.png",
        )

    def test_higgsfield_asset_url_rejects_unknown_response(self):
        with self.assertRaises(ValueError):
            hf._asset_url({"status": "completed"})


if __name__ == "__main__":
    unittest.main()
