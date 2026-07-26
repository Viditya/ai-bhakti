# Loop Instructions

## Loop type: goal-based
Run until: every video in the current TASK.md batch reaches
`pending_human_approval` OR `blocked`, OR the batch-level stop condition
in TASK.md triggers.

## Per-tick procedure (one tick = one sub-agent delegation)
1. Read PROGRESS.md top to bottom. Pick the first video whose status is
   NOT `pending_human_approval`, `approved`, `uploaded`, or `blocked`.
2. Look up that status in the status machine (top of PROGRESS.md) to
   determine the next agent to call and what it needs as input.
3. Call that ONE sub-agent with its required input (see its SKILL.md for
   exact schema).
4. Immediately write the result to that video's block in PROGRESS.md.
   Update `status`, relevant paths/scores, `last_updated_by`, and
   `spend_usd` if the step cost money.
5. If this step was a gate (script or consistency) and it FAILED:
   - increment the relevant counter in `attempt_counts`
   - if counter < max_retry_per_gate (from TASK.md): set status back to
     the pre-gate state, attach the failure feedback for the next attempt
   - if counter >= max_retry_per_gate: set status to `blocked`, write
     the reason in `notes`, move on
6. Go to next tick (next video, or same video if it just moved forward).

## Self-verification rules (must be checked explicitly, not eyeballed)
- Sutradhar's output: is narration_duration_estimate_sec within the
  target_length_sec range from TASK.md? Do all 5 titles match the
  question+emoji pattern? Both must be true.
- Parakh's script scores: all 5 axis scores present and numeric,
  overall computed with the documented weights (see parakh/SKILL.md),
  not eyeballed as "looks like an 8."
- Chitrkar's shots: consistency score computed against the ACTUAL
  character_lock file, not assumed.
- Sampadak's output: run the actual verification functions in
  scripts/ffmpeg_assemble.py (duration match, watermark detection) —
  these are real functions, call them, don't approximate.

## What breaks this loop (know these so you can recognize them)
- Calling a sub-agent without updating PROGRESS.md immediately after —
  this loses state on restart.
- Retrying the same gate indefinitely without incrementing/checking
  attempt_counts — this is the AutoGPT-style infinite loop failure mode.
- Silently lowering a gate's threshold instead of respecting `blocked` —
  if a video is stuck, that's information (probably a SKILL.md needs
  editing), not something to route around.
