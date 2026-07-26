# AI Bhakti — Start Here

## What's real vs. what's a stub in this package (read this before anything else)

**Actually working, tested code:**
- `scripts/ffmpeg_assemble.py` — all four verification functions
  (duration match, watermark presence, blank-frame detection, resolution
  check) are implemented and were tested end-to-end against a generated
  sample clip (see `tests/test_ffmpeg_assemble.py` — run it yourself to
  confirm: `python3 tests/test_ffmpeg_assemble.py`). Requires `ffmpeg`,
  `ffprobe`, and `Pillow` (`pip install pillow --break-system-packages`
  if not already present).
- `scripts/youtube_upload.py` — the human-approval gate is real and
  tested (refuses without both `--confirmed` AND `human_approved: true`
  in PROGRESS.md). The actual YouTube Data API upload call is
  intentionally NOT implemented — see the TODO in that file.

**Stubs that will raise `NotImplementedError` on purpose:**
- `scripts/higgsfield_client.py` — the method shapes are a reasonable
  guess, NOT verified against Higgsfield's current API. Confirm their
  docs before implementing.
- `scripts/elevenlabs_client.py` — same caveat, lower risk since
  ElevenLabs' API is more stable, but Hindi voice availability and exact
  params still need confirming.

**Documentation/config (no code, but load-bearing for Claude Code):**
- `VISION.md`, `CLAUDE.md`, `TASK.md`, `PROGRESS.md`, `LOOP_INSTRUCTIONS.md`
- `.claude/skills/*/SKILL.md` — five agent definitions

## Exact setup steps

1. Unzip this into your project location (or use as the whole project root).
2. `cd ai-bhakti`
3. `pip install pillow --break-system-packages` (if not already installed)
4. Confirm ffmpeg/ffprobe are on PATH: `which ffmpeg ffprobe`
5. Run the test to prove the verification logic works on your machine:
   `python3 tests/test_ffmpeg_assemble.py`
   You should see "ALL TESTS PASSED" at the end.
6. Open this folder in Claude Code (`claude` in this directory). It will
   pick up `CLAUDE.md` automatically.
7. Edit `TASK.md` with your first real story premise.
8. Populate `references/character_locks/` with at least one reference
   image before running anything involving a recurring deity.
9. Before touching `higgsfield_client.py` or `elevenlabs_client.py`, tell
   Claude Code to check current API docs for each — do not implement
   against the guessed interface shapes without verifying first.
10. Start with ONE video end-to-end, manually stepping through each
    agent yourself before letting the orchestrator run the full loop
    unattended. This is the same "prove each piece in isolation first"
    principle from the progressive-prompting approach.

## What I did NOT do, and why
- I did not fabricate Higgsfield/ElevenLabs API details to make the
  stubs "look complete" — a plausible-looking but wrong API call is
  worse than an honest `NotImplementedError`, because it fails silently
  or confusingly instead of loudly.
- I did not build the YouTube Data API upload call itself — that
  requires your actual Google Cloud project, OAuth consent screen, and
  possibly a quota increase request, which only you can set up.
- I did not include real generation API keys or credentials anywhere in
  this package, obviously — wire those in via environment variables on
  your machine, not hardcoded in these files.
