---
name: chitrkar
description: Generates cinematic AI visuals per shot using Higgsfield, conditioned on a locked character reference. Use after a script passes Parakh's Mode A gate.
---

# Chitrkar — Visual Generation

## Input
```json
{
  "script_hindi": "string",
  "shot_breakdown": ["shot 1 description", "shot 2 description", "..."],
  "character_lock_path": "string — path under references/character_locks/"
}
```

## Output
```json
{
  "shot_image_paths": ["path1", "path2"],
  "generation_params": {"seed": 0, "reference_used": "path", "prompt": "string"}
}
```

## Rules
- ALWAYS condition generation on `character_lock_path` for any shot
  featuring a recurring deity. Never generate such a shot "from scratch."
  This is the single biggest lever for closing the consistency gap versus
  benchmark channels.
- Style constants (brand, not a per-shot creative decision): warm gold/
  amber color grade, cinematic close-up framing, dramatic single-subject
  composition. Leave watermark space (bottom-right) — Sampadak adds the
  actual watermark later, don't burn one in yourself.
- A fixed seed alone does NOT guarantee identity consistency across
  different shots/prompts — identity comes from the reference-image
  conditioning method, not the seed. Don't rely on seed-matching as your
  consistency strategy.
- Store every `generation_params` used in
  `outputs/<video_id>/shots/generation_log.json` so results are
  reproducible and debuggable later.
- Before writing scripts/higgsfield_client.py or changing how conditioning
  works, check Higgsfield's current API docs — do not assume prior
  capabilities are still accurate; this space changes quickly.

## Do NOT
- Do not proceed to the next shot if Parakh's Mode B check on a prior
  shot in this same batch already flagged a consistency failure — fix
  that shot first.
- Do not silently swap in a different reference image if the intended
  one fails to load — stop and report the error.
