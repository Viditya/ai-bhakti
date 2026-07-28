"""Deterministic Hindi text checks used by the Bhashavid gate."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


DEVANAGARI = re.compile(r"[\u0900-\u097f]")
DETACHED_MARK = re.compile(r"(?:^|\s)[\u093a-\u094f\u0951-\u0957]")
MOJIBAKE_MARKERS = ("à¤", "Ã", "â€", "\ufffd")
KNOWN_CORRECTIONS = {
    "मूर्छित": "मूर्च्छित",
    "हिंन्दी": "हिंदी",
}


def iter_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")


def check_text(path: str, text: str) -> list[dict[str, str]]:
    if not DEVANAGARI.search(text):
        return []

    issues: list[dict[str, str]] = []
    if unicodedata.normalize("NFC", text) != text:
        issues.append(
            {
                "path": path,
                "category": "unicode",
                "severity": "high",
                "original": text,
                "suggested": unicodedata.normalize("NFC", text),
                "explanation": "Hindi text must be stored in NFC normalization.",
            }
        )
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        issues.append(
            {
                "path": path,
                "category": "unicode",
                "severity": "critical",
                "original": text,
                "suggested": "",
                "explanation": "The text contains mojibake or a replacement character.",
            }
        )
    if DETACHED_MARK.search(text):
        issues.append(
            {
                "path": path,
                "category": "matra",
                "severity": "critical",
                "original": text,
                "suggested": "",
                "explanation": "A Devanagari combining mark is detached from its base character.",
            }
        )
    if "  " in text:
        issues.append(
            {
                "path": path,
                "category": "consistency",
                "severity": "medium",
                "original": text,
                "suggested": re.sub(r" {2,}", " ", text),
                "explanation": "Repeated spaces can create misleading gaps in rendered Hindi.",
            }
        )
    for incorrect, correction in KNOWN_CORRECTIONS.items():
        if incorrect in text:
            issues.append(
                {
                    "path": path,
                    "category": "spelling",
                    "severity": "high",
                    "original": text,
                    "suggested": text.replace(incorrect, correction),
                    "explanation": f"Use the standard spelling “{correction}”.",
                }
            )
    return issues


def load_content(path: Path) -> Any:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")


def check_paths(paths: Iterable[Path]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for file_path in paths:
        content = load_content(file_path)
        for value_path, text in iter_strings(content, str(file_path)):
            issues.extend(check_text(value_path, text))
    return issues


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    issues = check_paths(args.paths)
    payload = {"pass": not any(i["severity"] in {"critical", "high"} for i in issues), "issues": issues}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for issue in issues:
            print(f"{issue['severity']}: {issue['path']}: {issue['explanation']}")
        print("PASS" if payload["pass"] else "FAIL")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
