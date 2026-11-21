
def detect_moments(
    transcription: dict,
    min_duration: float = 30.0,
    max_duration: float = 50.0,
    window_step: float = 10.0
) -> list:
    """Generate overlapping candidate moments from a transcript."""

    segments = transcription.get("segments", [])

    if not segments:
        return []

    video_end = max(segment["end"] for segment in segments)

    moments = []
    start = 0.0

    while start + min_duration <= video_end:

        end = min(start + max_duration, video_end)

        if end - start < min_duration:
            break

        selected_segments = [
            segment for segment in segments
            if segment["end"] > start
            and segment["start"] < end
        ]

        text = " ".join(
            segment["text"].strip()
            for segment in selected_segments
        )

        if text.strip():
            moments.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "duration": round(end - start, 2),
                "text": text
            })

        start += window_step

    return moments
