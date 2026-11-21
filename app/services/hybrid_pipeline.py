
import logging
from pathlib import Path

from app.services.ranker import rank_moments
from app.services.multi_frame_analyzer import analyze_multiple_frames
from app.services.hybrid_ranker import calculate_hybrid_score
from app.services.frame_extractor import get_video_duration
from app.services.motion_detector import analyze_motion


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
    """Validate, rank, visually analyze and measure candidate motion."""

    if not candidates:
        logger.warning("No candidates received.")
        return []

    if frame_count < 1:
        raise ValueError("frame_count must be at least 1.")

    if visual_top_n < 1:
        raise ValueError("visual_top_n must be at least 1.")

    if not 0 <= overlap_threshold <= 1:
        raise ValueError("overlap_threshold must be between 0 and 1.")

    video = Path(video_path)

    if not video.is_file():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    video_duration = get_video_duration(str(video))

    logger.info("Video duration: %.2f seconds", video_duration)
    logger.info("===== HYBRID RANKING STARTED =====")
    logger.info("Input candidates: %d", len(candidates))

    prepared_candidates = []

    for moment in candidates:
        start = moment.get("start")
        end = moment.get("end")

        if not isinstance(start, (int, float)):
            continue

        if not isinstance(end, (int, float)):
            continue

        if start < 0 or end <= start:
            continue

        if end > video_duration:
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

    transcript_ranked = rank_moments(prepared_candidates)

    logger.info(
        "Transcript ranking completed: %d candidates",
        len(transcript_ranked)
    )

    unique_candidates = remove_overlapping_candidates(
        transcript_ranked,
        overlap_threshold=overlap_threshold
    )

    logger.info(
        "Duplicates removed: %d",
        len(transcript_ranked) - len(unique_candidates)
    )

    selected_candidates = unique_candidates[:visual_top_n]

    logger.info(
        "Selected for visual analysis: %d",
        len(selected_candidates)
    )

    hybrid_results = []
    failed_count = 0

    for index, moment in enumerate(selected_candidates, start=1):
        logger.info(
            "Analyzing candidate %d/%d",
            index,
            len(selected_candidates)
        )

        try:
            visual_result = analyze_multiple_frames(
                str(video),
                moment["start"],
                moment["end"],
                frame_count=frame_count
            )

            motion_result = analyze_motion(
                str(video),
                moment["start"],
                moment["end"]
            )

            hybrid_score = calculate_hybrid_score(
                transcript_score=moment["score"],
                visual_score=visual_result["visual_score"],
                gameplay_ratio=visual_result["gameplay_ratio"],
                motion_score=motion_result["motion_score"]
            )

            hybrid_results.append({
                **moment,
                **hybrid_score,
                "motion_ratio": motion_result["motion_ratio"],
                "motion_samples": motion_result["samples_compared"],
                "visual_frames_analyzed": visual_result["frames_analyzed"]
            })

        except Exception:
            failed_count += 1
            logger.exception(
                "Candidate analysis failed for candidate %d",
                index
            )

    hybrid_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    logger.info("===== HYBRID PIPELINE SUMMARY =====")
    logger.info("Input: %d", len(candidates))
    logger.info("Valid: %d", len(prepared_candidates))
    logger.info("Unique: %d", len(unique_candidates))
    logger.info("Selected: %d", len(selected_candidates))
    logger.info("Analysis failures: %d", failed_count)
    logger.info("Successful results: %d", len(hybrid_results))

    return hybrid_results

