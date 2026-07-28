# Current Task

_Edit this file at the start of each work session. This is the only file
you should need to touch to start a new batch of videos._

## Batch goal
Produce 3 Shorts, all featuring Hanuman only (single character_lock keeps
the first batch's consistency-gate risk low while the pipeline is still
unproven end-to-end):
1. हनुमान जी ने बचपन में सूर्य को फल समझकर निगलने की कोशिश क्यों की थी?
2. रामायण खत्म हुए हज़ारों साल हो गए, फिर भी हनुमान जी आज भी धरती पर क्यों मौजूद हैं?
3. सीता माता ने हनुमान जी को ऐसा कौन सा वरदान दिया था जो आज भी काम करता है?

## Constraints for this batch
- character_lock: references/character_locks/hanuman_v1.png
  — DOES NOT EXIST YET. Blocking prerequisite: before Chitrkar can run on
  any of these 3 premises, populate this file per
  references/character_locks/README.md. train_character_reference() in
  scripts/higgsfield_client.py is unimplemented (endpoint unconfirmed —
  see that file's docstring), so this cannot be automated yet; either (a)
  Viditya supplies/approves a reference image, or (b) a Soul ID is created
  manually via the Higgsfield dashboard/CLI first.
- Credentials and provider selections are not yet set on this machine:
  HIGGSFIELD_API_KEY, HIGGSFIELD_API_KEY_SECRET, HIGGSFIELD_SOUL_ID,
  ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID (see scripts/config.py).
  Sutradhar (script generation), Parakh (scoring), and Bhashavid (Hindi
  language/rendering QA) don't need these and can run now; Chitrkar and
  Sangeet are blocked until credentials are set.
- target_length_sec: [40, 60]
- max_retry_per_gate: 3
- max_spend_per_video_usd: 5

## Stop condition for this batch
All videos reach "pending_human_approval" in PROGRESS.md, OR
any single video exhausts its retry cap 3 times on the SAME gate —
if that happens, STOP the whole batch and flag it. Repeated failures on
the same gate signal a prompt/spec problem in that agent's SKILL.md, not
something to retry your way through.

## Plan for next session (written 2026-07-25, session paused here)

**Status when paused:** all 3 scripts for this batch are at `script_gate_passed`
in PROGRESS.md (video_001/002/003). Nothing else can proceed until the two
items below are done — this is a genuine external blocker, not a coding gap.

### Before starting next session (human action, not Claude Code)
1. Set the five values listed in `.env.example`, including the approved
   Higgsfield Soul ID and ElevenLabs voice ID.
2. Put a Hanuman reference into `references/character_locks/hanuman_v1.png`
   and create its Soul ID through the supported Higgsfield dashboard/CLI.
3. Put the approved transparent logo at
   `references/brand/watermark.png`.
4. Run `python scripts/preflight_check.py` yourself first. If it doesn't
   print `READY`, fix what it flags before invoking Claude Code again —
   don't spend a session re-discovering the same blockers.

### Execution plan once READY (in order)
1. Orchestrator (top-level Claude Code) reads VISION.md/PROGRESS.md/TASK.md
   as normal, confirms preflight is green, then for **each** video still
   at `script_gate_passed`:
   - Chitrkar: generate shots conditioned on `hanuman_v1.png` / the Soul ID.
   - Parakh Mode B: run `scripts/consistency_check.py` for real numbers,
     gate at `min_score >= 0.55`.
   - Sangeet: narration + BGM via the now-implemented ElevenLabs client.
   - Sampadak: assemble + run `scripts/ffmpeg_assemble.py verify_all()`.
   - Stop at `pending_human_approval` and write real `spend_usd` back to
     PROGRESS.md before touching the next video.
2. Do NOT let $5/video cap or 3-retry cap slide "just this once" — these
   are the actual safety rails, not suggestions (see VISION.md, TASK.md
   constraints above).

### Cost control for next session — use subagents, not inline skill calls
This session ran every Sutradhar/Parakh call **inline** in the main
conversation (via the Skill tool), which meant each skill's full SKILL.md
text plus all prior turns stayed in the same context window the whole
session — that's the main reason token spend was high, and it compounds
worse for Chitrkar/Sangeet since those steps involve larger
inputs/outputs (images, audio) than text scripts did.

Next session, delegate each production step to an isolated subagent via
the **Agent tool** instead, one per video per step:
- `Agent({ description: "Chitrkar shots for video_00X", prompt: "<the
  video's script + character_lock path + chitrkar/SKILL.md contents>",
  subagent_type: "general-purpose" })` — its context (image-generation
  back-and-forth, retries) stays isolated and doesn't bloat the
  orchestrator's own context.
- Same pattern for Bhashavid, Sangeet, and Sampadak.
- The orchestrator's job becomes: read PROGRESS.md → spawn ONE subagent
  for the next step → take its structured result → write it to
  PROGRESS.md → move on. This matches CLAUDE.md's own role definition
  ("Sub-agents... Each should run with its own isolated context") which
  this session did not actually follow.
- Run video_001/002/003's independent steps (e.g. Chitrkar for all 3) in
  **parallel** Agent calls where they don't depend on each other, per the
  Agent tool's own guidance — this reduces wall-clock, not token spend,
  but is worth doing since each video's shots don't depend on the others.

## Notes / decisions from last session
- 2026-07-25: Implemented scripts/higgsfield_client.py and
  scripts/elevenlabs_client.py for real against current docs (previously
  intentional NotImplementedError stubs). ElevenLabs client is fully
  implemented and confirmed against official docs. Higgsfield client's
  generate_shot() is implemented and confirmed (base URL, auth header
  format, async submit/poll pattern, image endpoint all confirmed from
  docs.higgsfield.ai); train_character_reference() is still
  NotImplementedError because the REST path for Soul ID creation isn't
  published anywhere found — only the official JS SDK's method signature
  is, not the HTTP path it calls. Also unconfirmed: whether
  platform.higgsfield.ai's soul/standard endpoint expects `soul_id` or
  `custom_reference_id` as the reference field — see
  HiggsfieldClient.reference_field_name, set explicitly once confirmed
  against your own account.
- Added requirements.txt (requests, pillow) and scripts/config.py
  (env-var credential loading, nothing hardcoded).
- Chose a single-deity (Hanuman) first batch deliberately, to isolate
  whether the pipeline works at all from whether multi-character
  consistency works.
- Next concrete blockers, in order: (1) set the three API credential env
  vars, (2) get a Hanuman reference image/Soul ID into
  references/character_locks/hanuman_v1.png, (3) run Sutradhar on premise
  1 manually (per README_START_HERE.md step 10 — prove one video
  end-to-end by hand before letting the full loop run unattended).
- Update: (3) is now done for all 3 videos in this batch — all passed
  Parakh Mode A (script_gate_passed in PROGRESS.md). video_001 needed 2
  attempts (originality/emotion), video_002 passed on attempt 1,
  video_003 needed 2 attempts (originality, and quoting a Chalisa line
  too verbatim).
- Also implemented scripts/consistency_check.py (face_recognition-based
  Mode B automation) since parakh/SKILL.md previously only allowed a
  manual eyeball fallback for shot-consistency scoring — that doesn't
  scale to daily production. Requires `pip install face_recognition`
  separately (needs a C++ build toolchain for dlib) — not in
  requirements.txt for that reason, see the comment there.
- Everything now genuinely blocked on (1) and (2) — no further
  orchestrator progress is possible without them, since Chitrkar and
  Sangeet both require live API calls, and Mode B needs real shots to
  score. These two require your action, not more coding.
