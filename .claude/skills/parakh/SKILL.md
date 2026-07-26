---
name: parakh
description: Scores scripts for virality potential (Mode A) and checks shot-to-shot character consistency (Mode B). Use Mode A as the gate before production begins, and Mode B as the gate before Sangeet/Sampadak proceed.
---

# Parakh — QA / Scoring Gate

## Mode A: Script gate

### Input
```json
{"script_hindi": "string", "titles": ["t1","t2","t3","t4","t5"]}
```

### Output (strict JSON)
```json
{
  "hook_score": 0,
  "emotion_score": 0,
  "retention_structure_score": 0,
  "length_fit_score": 0,
  "originality_score": 0,
  "overall": 0,
  "pass": false,
  "feedback": "string — specific and actionable, not generic"
}
```
`overall` = hook_score*0.35 + emotion_score*0.25 + retention_structure_score*0.2
          + length_fit_score*0.1 + originality_score*0.1
`pass` = true only if `overall >= 8`

### Scoring rubric — score every axis explicitly, do not skip any
- **hook_score**: Does the FIRST LINE work standalone as a scroll-stopper —
  a genuine curiosity gap or bold claim? Score low (0-3) for a generic or
  slow-building opener.
- **emotion_score**: high-arousal positive emotion (awe/reverence/wonder)
  scores high. Purely calm/informational narration scores low even if
  factually solid — arousal, not accuracy, drives this axis.
- **retention_structure_score**: is there a clear payoff and no flat/dead
  stretch in the middle?
- **length_fit_score**: penalize padding to hit a target length, or a
  rushed/cut-off resolution.
- **originality_score**: flag anything that reads as templated or
  mass-produced — this matters for platform policy risk, not just quality.
- `feedback` must name the SPECIFIC axis and line that's weakest, not
  "make it better."

## Mode B: Shot consistency gate

### Input
```json
{"reference_image_path": "string", "shot_image_paths": ["p1","p2",...]}
```

### Output
```json
{
  "consistency_scores": [0.0],
  "min_score": 0.0,
  "pass": false,
  "flagged_shots": ["path_of_any_shot_below_threshold"]
}
```
`pass` = true only if `min_score >= 0.55` (starting threshold — this is a
documented starting point from general identity-preservation benchmarks,
NOT tuned to this channel's actual visual style; retune after reviewing
your first batch manually).

### Rules
- Report the MINIMUM score across shots, never the mean — one badly
  inconsistent shot in an otherwise-good batch is still a failure a
  viewer will notice.
- Call scripts/consistency_check.py's check_consistency() to get the
  actual numbers — it implements this exact output contract via
  face_recognition (dlib). Only fall back to a manual eyeball check, and
  say so explicitly in the output, if that script errors (e.g.
  face_recognition isn't installed, or no face is detected in a shot —
  NoFaceFoundError) rather than fabricating a number.

## Do NOT
- Do not pass a script "because it's close enough" — output the actual
  number and let the orchestrator's threshold decide, not your judgment
  call layered on top of the number.
- Do not average away a single failing shot.
