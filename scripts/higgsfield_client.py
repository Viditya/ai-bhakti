"""
higgsfield_client.py — implemented against Higgsfield's current platform
API docs (confirmed 2026-07-25 via https://docs.higgsfield.ai/docs/how-to/introduction.md
and https://docs.higgsfield.ai/docs/guides/images.md), with one gap called
out explicitly below rather than guessed at.

Confirmed and implemented:
- Base URL: https://platform.higgsfield.ai
- Auth header: "Authorization: Key {api_key}:{api_key_secret}" (note this
  is a colon-joined pair, not a single bearer token)
- Async queue architecture: POST /{model_id} to submit -> {"request_id": ...}
  then GET /requests/{request_id}/status to poll until status is one of
  queued / in_progress / nsfw / failed / completed
- Image generation model path used here: higgsfield-ai/soul/standard
  (prompt, aspect_ratio, resolution are confirmed body fields)

NOT confirmed — do not treat as correct without checking your own account's
API console first:
- The exact request field name for character-reference conditioning.
  Sources disagree: Higgsfield's own CLI/wavespeed docs use `soul_id`,
  while the official higgsfield-js SDK's /v1/text2image/soul endpoint uses
  `custom_reference_id` + `custom_reference_strength` — these look like two
  different API surfaces (platform.higgsfield.ai model-path API vs a v1
  REST API), and no source confirms which field platform.higgsfield.ai's
  soul/standard endpoint actually expects. `reference_field_name` below is
  a constructor param so you can set it once you've confirmed it, instead
  of the code silently using a wrong field name.
- The REST endpoint to CREATE/train a Soul ID (character reference) from
  images. The official JS SDK exposes client.createSoulId({name,
  input_images}) but the raw HTTP path it calls is not shown in the SDK's
  public docs/README. train_character_reference() below is left as
  NotImplementedError for this reason — a wrong guessed path fails
  loudly here, which is safer than a plausible-looking wrong one.
"""

import time
from typing import Optional

import requests

API_BASE = "https://platform.higgsfield.ai"
TERMINAL_STATUSES = {"nsfw", "failed", "completed"}


class HiggsfieldClient:
    def __init__(
        self,
        api_key: str,
        api_key_secret: str,
        reference_field_name: str = "soul_id",
    ):
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.reference_field_name = reference_field_name

    def _headers(self) -> dict:
        return {
            "Authorization": f"Key {self.api_key}:{self.api_key_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def generate_shot(
        self,
        prompt: str,
        character_lock_ref_id: str,
        model_id: str = "higgsfield-ai/soul/standard",
        aspect_ratio: str = "9:16",
        resolution: str = "1080p",
        poll_interval_sec: float = 3.0,
        timeout_sec: float = 300.0,
    ) -> dict:
        """
        Submits a generation request conditioned on character_lock_ref_id
        (the trained Soul ID / reference for a locked character — obtain
        this via your Higgsfield account, since train_character_reference()
        here is unimplemented pending endpoint confirmation), then polls
        until terminal status.

        character_lock_ref_id is NOT a local file path — Soul ID reference
        conditioning takes a reference ID registered with Higgsfield, not a
        raw image path. If you only have a local reference image and no
        registered Soul ID yet, you must create one manually via the
        Higgsfield dashboard/CLI (`higgsfield soul-id create`) until
        train_character_reference() is implemented here.

        Returns: {"image_path": None, "request_id": str, "raw_response": dict}
        image_path is None because the completed response's asset URL still
        needs downloading by the caller (Chitrkar) — not fabricated here.
        """
        submit_url = f"{API_BASE}/{model_id}"
        body = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            self.reference_field_name: character_lock_ref_id,
        }
        submit_resp = requests.post(submit_url, headers=self._headers(), json=body, timeout=60)
        submit_resp.raise_for_status()
        request_id = submit_resp.json()["request_id"]

        status_url = f"{API_BASE}/requests/{request_id}/status"
        elapsed = 0.0
        while elapsed < timeout_sec:
            status_resp = requests.get(status_url, headers=self._headers(), timeout=30)
            status_resp.raise_for_status()
            data = status_resp.json()
            if data.get("status") in TERMINAL_STATUSES:
                if data["status"] != "completed":
                    raise RuntimeError(f"Higgsfield generation ended with status={data['status']}: {data}")
                return {"image_path": None, "request_id": request_id, "raw_response": data}
            time.sleep(poll_interval_sec)
            elapsed += poll_interval_sec

        raise TimeoutError(f"Higgsfield request {request_id} did not complete within {timeout_sec}s")

    def train_character_reference(self, reference_images: list) -> str:
        """
        Intended contract (payload shape confirmed via the official
        higgsfield-js SDK's createSoulId, see module docstring):
          {"name": <str>, "input_images": [{"type": "image_url",
           "image_url": <url>}, ...]}
        Returns a soul_id/reference id string usable in generate_shot().

        Left unimplemented because the raw REST endpoint path for this
        call is not confirmed from public docs — only the SDK method
        signature is. Confirm the path (check your Higgsfield API
        dashboard or contact support) before implementing.
        """
        raise NotImplementedError(
            "Payload shape is known (see docstring) but the REST endpoint "
            "path for Soul ID creation is not confirmed. Verify it against "
            "your Higgsfield account's API reference before implementing."
        )
