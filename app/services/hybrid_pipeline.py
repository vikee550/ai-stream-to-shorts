import logging
import logging

from app.services.ranker import rank_moments
from app.services.multi_frame_analyzer import analyze_multiple_frames
from app.services.hybrid_ranker import calculate_hybrid_score


logger = logging.getLogger(__name__)


def remove_overlapping_candidates(
    candidates: list,
    overlap_threshold: float = 0.5
) -> list:
    """Keep the highest-ranked candidate among overlapping moments."""

    if not 0 <= overlap_threshold <= 1:
        raise ValueError("overlap_threshold must be between 0 and 1.")

    selected = []

    for candidate in candidates:
        start = candidate["start"]
        end = candidate["end"]

        if end <= start:
            continue

        is_duplicate = False

        for existing in selected:
            overlap_start = max(start, existing["start"])
            overlap_end = min(end, existing["end"])
            overlap = max(0, overlap_end - overlap_start)

            shorter_duration = min(
                end - start,
                existing["end"] - existing["start"]
            )

            overlap_ratio = overlap / shorter_duration

            if overlap_ratio > overlap_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            selected.append(candidate)

    return selected


def rank_hybrid_candidates(
    video_path: str,
    candidates: list,
    frame_count: int = 4,
    visual_top_n: int = 5,
    overlap_threshold: float = 0.5
) -> list:
    """Rank transcript candidates, remove duplicates, then analyze visually."""

    if not candidates:
        logger.warning("No candidates received.")
        return []

    if visual_top_n < 1:
        raise ValueError("visual_top_n must be at least 1.")

    logger.info("===== HYBRID RANKING STARTED =====")
    logger.info("Input candidates: %d", len(candidates))

    # Step 1: Validate candidates.
    prepared_candidates = []

    for moment in candidates:
        start = moment.get("start")
        end = moment.get("end")

        if not isinstance(start, (int, float)):
            continue

        if not isinstance(end, (int, float)):
            continue

        duration = end - start

        if duration < 30 or duration > 50:
            continue

        prepared_candidates.append({
            **moment,
            "duration": duration
        })

    invalid_count = len(candidates) - len(prepared_candidates)

    logger.info(
        "Valid candidates: %d | Invalid candidates: %d",
        len(prepared_candidates),
        invalid_count
    )

    if not prepared_candidates:
        logger.warning("No valid candidates available.")
        return []

    # Step 2: Transcript ranking.
    transcript_ranked = rank_moments(prepared_candidates)

    logger.info("Transcript ranking completed: %d candidates", len(transcript_ranked))

    # Step 3: Remove duplicates.
    unique_candidates = remove_overlapping_candidates(
        transcript_ranked,
        overlap_threshold=overlap_threshold
    )

    logger.info(
        "Duplicates removed: %d",
        len(transcript_ranked) - len(unique_candidates)
    )

    # Step 4: Select top candidates.
    selected_candidates = unique_candidates[:visual_top_n]

    logger.info(
        "Selected for visual analysis: %d",
        len(selected_candidates)
    )

    hybrid_results = []
    failed_count = 0

    # Step 5: Visual analysis and hybrid scoring.
    for index, moment in enumerate(selected_candidates, start=1):
        logger.info(
            "Analyzing candidate %d/%d",
            index,
            len(selected_candidates)
        )

        try:
            visual_result = analyze_multiple_frames(
                video_path,
                moment["start"],
                moment["end"],
                frame_count=frame_count
            )

            hybrid_score = calculate_hybrid_score(
                transcript_score=moment["score"],
                visual_score=visual_result["visual_score"],
                gameplay_ratio=visual_result["gameplay_ratio"]
            )

            hybrid_results.append({
                **moment,
                **hybrid_score,
                "visual_frames_analyzed": visual_result["frames_analyzed"]
            })

        except Exception:
            failed_count += 1
            logger.exception("Visual analysis failed for candidate %d", index)

    # Step 6: Final summary.
    hybrid_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    logger.info("===== HYBRID PIPELINE SUMMARY =====")
    logger.info("Input: %d", len(candidates))
    logger.info("Valid: %d", len(prepared_candidates))
    logger.info("Unique: %d", len(unique_candidates))
    logger.info("Visually selected: %d", len(selected_candidates))
    logger.info("Visual failures: %d", failed_count)
    logger.info("Successful results: %d", len(hybrid_results))

    return hybrid_results
