def create_transcript_windows(
    segments: list,
    window_seconds: int = 60
) -> list:
    """Group transcript segments into fixed time windows."""

    if not segments:
        return []

    windows = {}

    for segment in segments:
        start = segment["start"]
        window_start = int(start // window_seconds) * window_seconds

        windows.setdefault(window_start, []).append(segment)

    results = []

    for start, items in sorted(windows.items()):
        results.append({
            "start": start,
            "end": start + window_seconds,
            "text": " ".join(item["text"] for item in items)
        })

    return results
