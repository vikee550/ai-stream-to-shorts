def calculate_hybrid_score(
    transcript_score: int,
    visual_score: int,
    gameplay_ratio: float,
    motion_score: float = 0,
    audio_score: float = 0
) -> dict:
    """Combine transcript, visual, motion and audio evidence."""

    transcript_score = max(0, min(100, transcript_score))
    visual_score = max(0, min(100, visual_score))
    motion_score = max(0, min(100, motion_score))
    audio_score = max(0, min(100, audio_score))
    gameplay_ratio = max(0.0, min(1.0, gameplay_ratio))

    final_score = round(
        transcript_score * 0.65
        + visual_score * 0.20
        + motion_score * 0.10
        + audio_score * 0.05
    )

    return {
        "transcript_score": transcript_score,
        "visual_score": visual_score,
        "motion_score": round(motion_score, 2),
        "audio_score": round(audio_score, 2),
        "gameplay_ratio": round(gameplay_ratio, 2),
        "hybrid_score": final_score
    }
