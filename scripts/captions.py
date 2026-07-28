"""Create a reviewable first-pass SRT when word timestamps are unavailable."""

from pathlib import Path


def _timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def _chunks(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and len(candidate) > max_chars:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def write_even_srt(
    text: str,
    duration_sec: float,
    output_path: str,
    *,
    max_chars: int = 32,
) -> str:
    """Split text into readable cards and distribute them by character count.

    This is a deterministic fallback, not word-level transcription. A human
    must review timing before publication.
    """
    if duration_sec <= 0:
        raise ValueError("duration_sec must be positive")
    chunks = _chunks(text.strip(), max_chars)
    if not chunks:
        raise ValueError("caption text must not be empty")
    total_weight = sum(max(1, len(chunk)) for chunk in chunks)
    elapsed = 0.0
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        start = elapsed
        elapsed += duration_sec * max(1, len(chunk)) / total_weight
        end = duration_sec if index == len(chunks) else elapsed
        blocks.append(
            f"{index}\n{_timestamp(start)} --> {_timestamp(end)}\n{chunk}\n"
        )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(blocks), encoding="utf-8")
    return str(destination)
