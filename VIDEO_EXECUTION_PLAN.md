# First paid video test

## Objective

Turn the completed eight-panel **Hanumanji's Tail in Lanka** comic into one vertical 1080x1920 pilot video. This is a controlled provider test, not an automatic publication run.

## Ready now

- Eight approved comic panels and a publishable PDF.
- Locked mature Hanuman, Ravana, Sita, and Vibhishana references.
- Transparent watermark plus portable FFmpeg and ffprobe.
- Local assembly and verification code; no credential is embedded in it.

## Credentials to add later

Set only in the local environment or .env: HIGGSFIELD_API_KEY, HIGGSFIELD_API_KEY_SECRET, HIGGSFIELD_SOUL_ID, ELEVENLABS_API_KEY, and ELEVENLABS_VOICE_ID. Then run python scripts/preflight_check.py.

## Controlled run order

1. A fluent Hindi reviewer approves the eight captions and narration text.
2. Install the pinned official SDK with pnpm install, confirm the Higgsfield Soul ID from the mature Hanuman lock, then create one short image-to-video motion test from panel 1 using scripts/higgsfield_video.mjs.
3. Human-review identity drift and artefacts before paying for the remaining panels.
4. Generate and approve one Hindi ElevenLabs narration.
5. Assemble reviewed clips, narration, captions, and watermark; run verify_all().
6. Stop at pending_human_approval. Upload is a later explicit action.

## Spend guardrails

- Start with one panel and one narration call.
- Do not run parallel generations until that review passes.
- Record each provider cost in PROGRESS.md.
- Never upload or publish during this test.
