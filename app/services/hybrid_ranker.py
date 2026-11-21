def calculate_hybrid_score(
    transcript_score: int,
    visual_score: int,
    gameplay_ratio: float
) -> dict:
    """
    Combine transcript and visual evidence.

    Provisional weights:
    Transcript: 85%
    Visual: 15%

    Gameplay ratio is metadata, not visual confidence.
    """

    transcript_score = max(0, min(100, transcript_score))
    visual_score = max(0, min(100, visual_score))
    gameplay_ratio = max(0.0, min(1.0, gameplay_ratio))

    final_score = round(
        transcript_score * 0.85
        + visual_score * 0.15
    )

    return {
        "transcript_score": transcript_score,
        "visual_score": visual_score,
        "gameplay_ratio": round(gameplay_ratio, 2),
        "hybrid_score": final_score
    }
