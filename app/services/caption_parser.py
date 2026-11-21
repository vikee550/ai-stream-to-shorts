import re
import html
from pathlib import Path


TIMESTAMP_PATTERN = re.compile(
    r"(\d{2,}):(\d{2}):(\d{2})\.(\d{3})"
)


def to_seconds(value):
    match = TIMESTAMP_PATTERN.search(value)
    if not match:
        return None

    h, m, s, ms = map(int, match.groups())
    return h * 3600 + m * 60 + s + ms / 1000


def remove_overlap(previous, current):
    old = previous.split()
    new = current.split()

    for size in range(min(len(old), len(new)), 0, -1):
        a = [re.sub(r"\W", "", x).lower() for x in old[-size:]]
        b = [re.sub(r"\W", "", x).lower() for x in new[:size]]

        if a == b:
            return " ".join(new[size:]).strip()

    return current


def parse_vtt(file_path: str) -> list:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(file_path)

    content = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", content.strip())

    segments = []
    previous_text = ""

    for block in blocks:
        lines = block.strip().splitlines()

        timestamp = next(
            (line for line in lines if "-->" in line),
            None
        )

        if not timestamp:
            continue

        times = timestamp.split("-->")

        if len(times) != 2:
            continue

        start = to_seconds(times[0])
        end = to_seconds(times[1])

        if start is None or end is None or end - start < 0.05:
            continue

        text_lines = lines[lines.index(timestamp) + 1:]
        text = " ".join(line.strip() for line in text_lines)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            continue

        clean_text = remove_overlap(previous_text, text)

        if not clean_text:
            continue

        segments.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "text": clean_text
        })

        previous_text = text

    return segments
