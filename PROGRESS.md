# Progress Log

## Status machine (reference — every video's `status` must be one of these)
`new` -> `script_generated` -> `script_gate_failed` (loop back to script_generated
or -> `blocked` if retries exhausted) -> `script_gate_passed` ->
`shots_generated` -> `consistency_gate_failed` (loop back or -> `blocked`) ->
`consistency_gate_passed` -> `audio_generated` -> `assembled` ->
`pending_human_approval` -> `approved` -> `uploaded`
(or `blocked` at any gate after retries exhausted)

## Template for a new video entry — copy this block per video
```
## video_XXX
- premise:
- status: new
- attempt_counts: {script_gate: 0, consistency_gate: 0}
- script_path:
- hook_score:
- titles_path:
- character_lock:
- shot_paths: []
- consistency_min_score:
- narration_audio_path:
- bgm_audio_path:
- final_video_path:
- verification: {duration_match: null, watermark_present: null}
- human_approved: false
- spend_usd: 0
- last_updated_by:
- notes:
```

---

## Active videos

## video_001
- premise: हनुमान जी ने बचपन में सूर्य को फल समझकर निगलने की कोशिश क्यों की थी?
- status: script_gate_passed
- attempt_counts: {script_gate: 1, consistency_gate: 0}
- script_path: outputs/video_001/script_v2.json
- hook_score: 9 (overall 8.35, PASSED)
- titles_path: outputs/video_001/script_v2.json (titles field)
- character_lock: references/character_locks/hanuman_v1.png
- shot_paths: []
- consistency_min_score:
- narration_audio_path:
- bgm_audio_path:
- final_video_path:
- verification: {duration_match: null, watermark_present: null}
- human_approved: false
- spend_usd: 0
- last_updated_by: parakh
- notes: script_v1 FAILED Parakh Mode A (overall 7.65, weak originality+emotion) on attempt 1. script_v2 addressed feedback (Indra's-shock reframing, added sensory beats) and PASSED on attempt 2/3: hook=9 emotion=8 retention=8 length=9 originality=7, overall=8.35. Next step: Chitrkar (shots) + Sangeet (narration), both BLOCKED — see TASK.md blockers (no HIGGSFIELD/ELEVENLABS credentials, no hanuman_v1.png character lock yet).

## video_002
- premise: रामायण खत्म हुए हज़ारों साल हो गए, फिर भी हनुमान जी आज भी धरती पर क्यों मौजूद हैं?
- status: script_gate_passed
- attempt_counts: {script_gate: 0, consistency_gate: 0}
- script_path: outputs/video_002/script_v1.json
- hook_score: 9 (overall 8.25, PASSED)
- titles_path: outputs/video_002/script_v1.json (titles field)
- character_lock: references/character_locks/hanuman_v1.png
- shot_paths: []
- consistency_min_score:
- narration_audio_path:
- bgm_audio_path:
- final_video_path:
- verification: {duration_match: null, watermark_present: null}
- human_approved: false
- spend_usd: 0
- last_updated_by: parakh
- notes: Passed Parakh Mode A on attempt 1/3 (hook=9 emotion=8 retention=7 length=9 originality=8, overall=8.25). retention_structure flagged as relatively weak (list-like middle) but above gate. Next step: Chitrkar + Sangeet, both BLOCKED — same credential/character-lock blockers as video_001.

## video_003
- premise: सीता माता ने हनुमान जी को ऐसा कौन सा वरदान दिया था जो आज भी काम करता है?
- status: script_gate_passed
- attempt_counts: {script_gate: 1, consistency_gate: 0}
- script_path: outputs/video_003/script_v2.json
- hook_score: 9 (overall 8.35, PASSED)
- titles_path: outputs/video_003/script_v2.json (titles field)
- character_lock: references/character_locks/hanuman_v1.png
- shot_paths: []
- consistency_min_score:
- narration_audio_path:
- bgm_audio_path:
- final_video_path:
- verification: {duration_match: null, watermark_present: null}
- human_approved: false
- spend_usd: 0
- last_updated_by: parakh
- notes: script_v1 FAILED Parakh Mode A (overall 7.65 — declarative hook, quoted Chalisa line verbatim, weak originality). script_v2 reframed to open from a devotee's felt experience instead of announcing the boon, PASSED on attempt 2/3 (overall 8.35). Next step: Chitrkar + Sangeet, both BLOCKED — same credential/character-lock blockers as video_001/002.
