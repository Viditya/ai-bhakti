---
name: chitrkar
description: Generates cinematic AI visuals per shot using Higgsfield, conditioned on exact age-aware character locks. Use after a script passes Parakh's Mode A gate.
---

# Chitrkar — Visual Generation

## Input

```json
{
  "script_hindi": "string",
  "shot_breakdown": ["shot 1 description", "shot 2 description"],
  "characters": [
    {
      "character_id": "hanuman",
      "age_stage": "child",
      "form_id": null,
      "character_lock_path": "references/character_locks/hanuman/child/reference_v1.png"
    }
  ]
}
```

## Output

```json
{
  "shot_image_paths": ["path1", "path2"],
  "generation_params": {
    "seed": 0,
    "references_used": [
      {
        "character_id": "hanuman",
        "age_stage": "child",
        "form_id": null,
        "path": "references/character_locks/hanuman/child/reference_v1.png"
      }
    ],
    "prompt": "string"
  }
}
```

## Rules

- Resolve every recurring character by the exact `character_id` and
  `age_stage` in `references/character_locks/manifest.json`. When a request
  includes `form_id`, resolve that exact locked form asset.
- Condition generation on that stage's or form's locked asset. Never generate a
  recurring character from scratch.
- Reject `candidate` assets and reject silent fallback to another age stage,
  base form, or nearby form.
- In multi-character shots, supply the lock for every visible recurring
  character, not only the lead.
- Preserve each manifest `identity_invariants` list. Permit only changes
  explicitly named in `allowed_age_changes`.
- Style constants: warm gold/amber color grade, cinematic close-up framing,
  dramatic single-subject composition. Leave watermark space bottom-right;
  Sampadak adds the actual watermark later.
- A fixed seed alone does not guarantee identity consistency. Identity comes
  from the reference-conditioning method.
- Store every generation parameter in
  `outputs/<video_id>/shots/generation_log.json`.
- Before changing Higgsfield conditioning, verify its current API
  documentation.

## Do not

- Do not proceed after Parakh Mode B flags a consistency failure.
- Do not silently swap references when a lock fails to load.
- Do not age a character merely through prompt wording. Every production age
  requires its own reviewed, locked asset and checksum.
- Do not portray a named divine form using the character's base-stage lock.
