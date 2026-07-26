"""
elevenlabs_client.py — implemented against ElevenLabs' current REST API
(confirmed 2026-07-25 via https://elevenlabs.io/docs/api-reference/text-to-speech/convert
and https://elevenlabs.io/docs/overview/models).

Confirmed contract:
- POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
- header: xi-api-key: <api_key>
- body: {"text": ..., "model_id": ..., "output_format" is a query param, not
  a body field, per the API reference}
- response: raw audio bytes (application/octet-stream)
- default model eleven_multilingual_v2 supports Hindi; language_code is not
  accepted by multilingual_v2, so we do not send it.

Still needs a one-time manual check before the first real run: confirm
your ElevenLabs account has a Hindi-capable voice_id (GET /v1/voices) —
this client does not pick a voice for you.
"""

import requests

from ffmpeg_assemble import _ffprobe_duration

API_BASE = "https://api.elevenlabs.io"


class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_narration(
        self,
        text_hindi: str,
        voice_id: str,
        output_path: str,
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
    ) -> dict:
        """
        Generates narration audio from Hindi text and writes it to
        output_path. Returns {"audio_path": output_path, "duration_sec": float}
        for the sangeet/SKILL.md duration-matching rule.
        """
        url = f"{API_BASE}/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        params = {"output_format": output_format}
        body = {"text": text_hindi, "model_id": model_id}

        response = requests.post(url, headers=headers, params=params, json=body, timeout=120)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        return {
            "audio_path": output_path,
            "duration_sec": _ffprobe_duration(output_path),
        }
