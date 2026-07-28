# AI Bhakti — Vision

## What this project is
A Hindi devotional YouTube Shorts automation pipeline producing content from
the Ramayana, Mahabharata, and Puranas, benchmarked against channels like
Dev Kathan Shorts (335K subscribers, 107 videos as of last research pass).

## Non-negotiables (do not treat these as optional/creative choices)
1. Every video with a recurring deity/character MUST resolve the exact
   `character_id` + `age_stage` from
   `references/character_locks/manifest.json` and use that locked reference.
   Never generate a recurring character from scratch or silently substitute
   a nearby age.
2. Every script MUST pass Parakh's hook-score gate (overall >= 8/10) before
   entering visual/audio production.
3. NO video is uploaded without a human setting `human_approved: true` in
   `PROGRESS.md` for that video_id. This is enforced in code
   (see scripts/youtube_upload.py), not just in instructions.
4. Brand constants: warm gold/amber cinematic color grade, consistent
   watermark (bottom-right), curiosity-gap Hindi titles with emoji,
   9:16 vertical, 1080x1920.

## Definition of "done" for one video
- hook_score >= 8/10 (Parakh)
- shot-to-shot character consistency >= threshold (Parakh, Mode B)
- |audio_duration - video_duration| < 0.5s (Sampadak, verified programmatically)
- watermark present in sampled frames (Sampadak, verified programmatically)
- human_approved: true (human, not an agent)

## What "good" looks like, concretely
First line of narration works as a standalone hook (no context needed).
Emotional register is awe/reverence/wonder, not flat/informational.
Visual identity of each deity is recognizably the SAME across every shot
in every video that features them.

## Known open questions (do not assume answers — verify before building on them)
- Exact Higgsfield API capabilities for reference-conditioned generation —
  check current docs before coding scripts/higgsfield_client.py.
- Real YouTube retention data for THIS channel does not exist yet — the
  scoring thresholds in this project are documented starting points from
  general research, not proven for this specific audience. Retune after
  30-50 published videos.
