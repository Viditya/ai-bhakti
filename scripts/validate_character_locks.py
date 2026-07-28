"""Validate the immutable, age-aware character-lock registry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "references" / "character_locks" / "manifest.json"
MIN_ASSET_BYTES = 100_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(path: Path = MANIFEST_PATH) -> list[str]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    declared_stages = set(manifest.get("age_stages", {}))

    for character_id, character in manifest.get("characters", {}).items():
        stages = character.get("stages", {})
        root_stage = character.get("identity_root_stage")
        if root_stage not in stages:
            errors.append(f"{character_id}: identity_root_stage is not locked")

        for age_stage, lock in stages.items():
            lock_id = f"{character_id}/{age_stage}"
            if age_stage not in declared_stages:
                errors.append(f"{lock_id}: undeclared age stage")
            if lock.get("status") != "locked":
                errors.append(f"{lock_id}: production stage is not locked")
            _validate_asset(lock_id, lock, errors)

        for index, candidate in enumerate(character.get("review_material", []), 1):
            candidate_id = f"{character_id}/candidate-{index}"
            if candidate.get("status") != "candidate":
                errors.append(f"{candidate_id}: review material must remain candidate")
            _validate_asset(candidate_id, candidate, errors)

    return errors


def _validate_asset(lock_id: str, record: dict, errors: list[str]) -> None:
    relative_asset = record.get("asset")
    expected_hash = record.get("sha256")
    if not relative_asset or not expected_hash:
        errors.append(f"{lock_id}: asset path and sha256 are required")
        return

    asset = ROOT / relative_asset
    if not asset.is_file():
        errors.append(f"{lock_id}: missing asset {relative_asset}")
        return
    if asset.stat().st_size < MIN_ASSET_BYTES:
        errors.append(f"{lock_id}: asset is unexpectedly small")
    actual_hash = sha256(asset)
    if actual_hash != expected_hash:
        errors.append(f"{lock_id}: checksum mismatch")


def main() -> int:
    errors = validate_manifest()
    if errors:
        print(json.dumps({"pass": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"pass": True, "errors": []}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
