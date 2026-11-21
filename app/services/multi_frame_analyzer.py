from statistics import median

from app.services.video_visual_pipeline import analyze_video_moment


def analyze_multiple_frames(
    video_path: str,
    start: float,
    end: float,
    frame_count: int = 4
) -> dict:
    """Analyze multiple frames and aggregate visual evidence."""

    if end <= start:
        raise ValueError("End timestamp must be greater than start.")

    if frame_count < 1:
        raise ValueError("Frame count must be at least 1.")

    duration = end - start

    timestamps = [
        start + duration * (i + 1) / (frame_count + 1)
        for i in range(frame_count)
    ]

    analyses = []

    for timestamp in timestamps:
        print(f"\nAnalyzing timestamp: {timestamp:.2f}")

        result = analyze_video_moment(video_path, timestamp)
        analyses.append(result)

    visual_scores = [
        item["visual_analysis"]["shorts_potential"]
        for item in analyses
    ]

    gameplay_frames = sum(
        item["visual_analysis"]["gameplay_visible"]
        for item in analyses
    )

    return {
        "start": start,
        "end": end,
        "frames_analyzed": len(analyses),
        "visual_score": round(median(visual_scores)),
        "gameplay_frames": gameplay_frames,
        "gameplay_ratio": round(
            gameplay_frames / len(analyses), 2
        ),
        "frame_analyses": analyses
    }
