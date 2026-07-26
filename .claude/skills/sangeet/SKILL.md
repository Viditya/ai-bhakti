---
name: sangeet
description: Generates narration audio and background music matched to script duration. Use after a script passes Parakh's gate, in parallel with Chitrkar.
---

# Sangeet — Audio Generation

## Input
```json
{"script_hindi": "string", "target_duration_sec": 0}
```

## Output
```json
{
  "narration_audio_path": "string",
  "bgm_audio_path": "string",
  "actual_duration_sec": 0
}
```

## Rules
- Narration duration must be within 0.5s of `target_duration_sec`. If it
  isn't after generation, REPORT the mismatch explicitly in the output —
  do not silently pass a mismatched duration forward.
- Background music should be devotional/instrumental and ducked well
  under the narration — most viewers watch muted with on-screen text,
  so audio is a secondary channel, not where to over-invest effort.
- Confirm current ElevenLabs/kie.ai/Suno API capabilities before writing
  or modifying scripts/elevenlabs_client.py — don't assume prior
  capabilities are still current.

## Do NOT
- Do not proceed if `actual_duration_sec` deviates more than 10% from
  target — flag to the orchestrator for a script-length adjustment loop
  (back to Sutradhar) instead of forcing a mismatched assembly.
