"""
config.py — reads generation API credentials from environment variables.
No credentials are ever hardcoded here or anywhere else in this project.

Required env vars (none are currently set on this machine as of last check —
set them before running Sangeet or Chitrkar for real):
  HIGGSFIELD_API_KEY
  HIGGSFIELD_API_KEY_SECRET
  HIGGSFIELD_SOUL_ID
  ELEVENLABS_API_KEY
  ELEVENLABS_VOICE_ID
"""

import os


class MissingCredentialError(Exception):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise MissingCredentialError(
            f"{name} is not set. Set it as an environment variable before "
            "calling this client — see scripts/config.py docstring."
        )
    return value


def higgsfield_credentials() -> tuple:
    return _require("HIGGSFIELD_API_KEY"), _require("HIGGSFIELD_API_KEY_SECRET")


def elevenlabs_credentials() -> str:
    return _require("ELEVENLABS_API_KEY")


def higgsfield_soul_id() -> str:
    return _require("HIGGSFIELD_SOUL_ID")


def elevenlabs_voice_id() -> str:
    return _require("ELEVENLABS_VOICE_ID")
