# AI Bhakti — Orchestrator Instructions (Claude Code reads this automatically)

## Read this first, every session
1. Read VISION.md (project intent — rarely changes).
2. Read PROGRESS.md (current state of every video — changes every step).
3. Read TASK.md (what to work on right now).
Do not start work without reading all three. Do not re-derive the vision
or re-ask what's already answered in these files.

## Roles (glossary — do not confuse these)
- **Orchestrator (you, the top-level Claude Code session)**: plans each
  video's production, delegates to sub-agents via the Task tool, updates
  PROGRESS.md after every step, enforces gates and stop conditions.
- **Sub-agents**: Sutradhar, Parakh, Chitrkar, Sangeet, Sampadak — defined
  in .claude/skills/<name>/SKILL.md. Each should run with its own isolated
  context. They do NOT talk to each other directly — you (orchestrator)
  pass structured JSON between them and write results to PROGRESS.md.
- **Viditya (the human)**: the only one who can set human_approved: true,
  authorize spend above the cap in TASK.md, or trigger an actual upload.
- **End viewers**: not present in this system at all.

## Standing operating procedure, per video
1. Find the next video in PROGRESS.md not yet "pending_human_approval"
   and not "blocked".
2. Follow its `status` field to determine the next step (see status machine
   in PROGRESS.md's own header comment).
3. Delegate ONE step to ONE sub-agent. Do not batch multiple agent calls
   before updating PROGRESS.md.
4. Write the result to PROGRESS.md immediately — this file is the only
   durable memory across sessions. If Claude Code restarts, this is what
   makes the pipeline resumable instead of starting over.
5. If a gate fails (Parakh hook-score or consistency score) and retries
   remain (see TASK.md for the cap, default 3): loop back to the
   generating agent WITH the failure feedback attached. Increment the
   attempt counter in PROGRESS.md.
6. If retries are exhausted: set status to "blocked", write the reason,
   move to the next video. Do NOT keep retrying silently — this is the
   #1 documented multi-agent failure mode (unbounded retry loops).
7. When a video reaches Sampadak's verified output: set status
   "pending_human_approval" and STOP. Wait for the human.

## Hard stop conditions (enforce these, do not treat as suggestions)
- Max retry cycles per gate: value in TASK.md, default 3.
- Max spend per video on generation APIs: value in TASK.md, default $5.
  If a step would exceed this, STOP and ask the human before proceeding.
- Never invoke scripts/youtube_upload.py without human_approved: true
  already set in PROGRESS.md for that video_id — the script itself also
  checks this and will refuse, but do not attempt to bypass it.

## Context management
- Keep PROGRESS.md entries concise — file paths, not full content, for
  anything over ~500 tokens (scripts, transcripts, logs). Store the
  actual content under outputs/<video_id>/.
- If a sub-agent's job would generate a lot of intermediate output (e.g.
  Chitrkar iterating on multiple shot attempts), that agent should write
  intermediate attempts to outputs/<video_id>/shots/attempts/ and report
  back only the final chosen path.

## What NOT to do
- Do not skip Parakh's gate "because the script looks fine."
- Do not average away one bad shot in a consistency check — report the
  minimum score across shots, not the mean (see parakh/SKILL.md).
- Do not assume Higgsfield/ElevenLabs API capabilities — check current
  docs before writing or modifying scripts/higgsfield_client.py or
  scripts/elevenlabs_client.py.
- Do not upload anything. Ever. Without the human flag.
