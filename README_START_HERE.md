# AI Bhakti — Start Here

## What's real vs. what's a stub in this package (read this before anything else)

**Actually working, tested code:**
- `scripts/ffmpeg_assemble.py` — assembles still shots, narration, optional
  BGM, watermark, and SRT captions into a vertical MP4, then exposes four
  verification functions (duration, watermark-region heuristic, blank
  frames, and resolution).
- `scripts/assemble_video.py` — supervised command-line assembly entry point.
- `scripts/captions.py` — deterministic first-pass SRT generation. Timing
  remains subject to human review.
- `scripts/youtube_upload.py` — the human-approval gate is real and
  tested, including UTF-8 progress files on Windows. The actual YouTube
  Data API upload remains intentionally unimplemented.
- `tests/test_pipeline_safety.py` — offline tests for approval, assembly
  command construction, and caption generation.

**Provider boundaries requiring live account validation:**
- `scripts/higgsfield_client.py` submits, polls, and downloads generated
  images. Soul ID creation remains outside this Python client; use the
  official Higgsfield CLI/dashboard and set `HIGGSFIELD_SOUL_ID`.
- `scripts/elevenlabs_client.py` generates narration and writes it
  durably. Select and approve a Hindi voice, then set
  `ELEVENLABS_VOICE_ID`.

**Documentation/config (no code, but load-bearing for Claude Code):**
- `VISION.md`, `CLAUDE.md`, `TASK.md`, `PROGRESS.md`, `LOOP_INSTRUCTIONS.md`
- `.claude/skills/*/SKILL.md` — six agent definitions, including Bhashavid's
  mandatory Hindi-language and Devanagari-rendering gate

## Exact setup steps

1. Unzip this into your project location (or use as the whole project root).
2. `cd ai-bhakti`
3. Create a virtual environment and run `pip install -r requirements.txt`.
4. Confirm `ffmpeg` and `ffprobe` are on PATH.
5. Run the test to prove the verification logic works on your machine:
   `python tests/test_ffmpeg_assemble.py`
   You should see "ALL TESTS PASSED" at the end.
6. Run the offline safety suite:
   `python -m unittest -v tests.test_pipeline_safety`
7. Open this folder in Claude Code (`claude` in this directory). It will
   pick up `CLAUDE.md` automatically.
8. Edit `TASK.md` with your first real story premise.
9. Add the approved character lock and brand watermark, create a Higgsfield
   Soul ID, select an ElevenLabs voice, and populate the variables shown in
   `.env.example`.
10. Before touching `higgsfield_client.py` or `elevenlabs_client.py`, tell
   Claude Code to check current API docs for each — do not implement
   against the guessed interface shapes without verifying first.
11. Start with ONE video end-to-end, manually stepping through each
    agent yourself before letting the orchestrator run the full loop
    unattended. This is the same "prove each piece in isolation first"
    principle from the progressive-prompting approach.

## What I did NOT do, and why
- I did not automate Soul ID training through an unverified private REST
  path. The supported CLI/dashboard remains the onboarding boundary.
- I did not build the YouTube Data API upload call itself — that
  requires your actual Google Cloud project, OAuth consent screen, and
  possibly a quota increase request, which only you can set up.
- I did not include real generation API keys or credentials anywhere in
  this package, obviously — wire those in via environment variables on
  your machine, not hardcoded in these files.
