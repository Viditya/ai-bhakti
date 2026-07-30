# Character locks

This directory is the canonical visual identity registry for recurring
characters. A production shot must resolve a character by both
`character_id` and `age_stage`, plus `form_id` when a story calls for a
distinct divine form. Using a nearby age, the base form in place of a named
form, or generating from scratch is not allowed.

## Lock hierarchy

1. `manifest.json` records the approved identity, age stage, asset path,
   invariant traits, and SHA-256 checksum.
2. `reference_vN.png` is an immutable production lock. Revisions create
   `reference_vN+1.png`; they never overwrite an earlier lock.
3. `candidate_vN.png` is review material and must not be used by Chitrkar.
4. A derived age stage inherits the root identity's facial geometry, palette,
   marks, and signature objects. Only the changes listed in its
   `allowed_age_changes` may vary.
5. A named form, such as Vishnu's Kurma or Mohini form, has its own immutable
   lock under `forms` and may not silently fall back to the base stage.

## Current registry

- Hanuman — child production lock; age-progression sheet is a candidate.
- Indra — ageless-adult production lock.
- Surya — ageless-adult production lock.
- Vayu — ageless-mature production lock.
- Vishnu — ageless-adult production lock; Kurma and Mohini form locks.
- Shiva — ageless-mature production lock.
- Lakshmi — ageless-adult production lock.
- Dhanvantari — ageless-adult production lock.
- Vasuki — ageless production lock.
- Bali — ageless-adult production lock.

Run the deterministic integrity check before visual generation:

```powershell
.\.venv\Scripts\python.exe scripts\validate_character_locks.py
```

The checker verifies paths, lock status, age-stage declarations, file sizes,
and exact hashes. Visual identity approval still requires human review.

## Age-stage policy

Use the fewest stages needed by a character's actual stories. Do not create
child or elder versions of an ageless deity merely to fill a matrix.

- `infant`
- `child`
- `adolescent`
- `young_adult`
- `mature_adult`
- `elder`
- `ageless`
- `ageless_adult`
- `ageless_mature`

For characters such as Rama, Krishna, Sita, Lakshmana, and the Pandavas,
create a root identity first, then derive only the story-required stages.
Each derived stage gets its own reviewed reference sheet and checksum.
