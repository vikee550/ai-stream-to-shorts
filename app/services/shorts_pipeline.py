from pathlib import Path

from app.services.pipeline import process_video
from app.services.moment_detector import detect_moments
from app.services.ranker import rank_moments
from app.services.clip_generator import create_clip
from app.services.vertical_converter import convert_to_vertical


def create_shorts(
    video_path: str,
    max_clips: int = 3,
    output_dir: str = "storage/clips"
) -> list:
    """Generate ranked vertical Shorts without subtitles."""

    print("\n===== AI SHORTS PIPELINE STARTED =====")

    print("\nStep 1: Processing original video...")
    result = process_video(video_path)
    transcription = result["transcription"]

    print("\nStep 2: Detecting moments...")
    moments = detect_moments(transcription)

    if not moments:
        print("No suitable moments detected.")
        return []

    print("Detected moments:", len(moments))

    print("\nStep 3: Ranking moments...")
    ranked_moments = rank_moments(moments)

    job_dir = Path(output_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    created_clips = []

    print("\nStep 4: Generating vertical Shorts without subtitles...")

    for index, moment in enumerate(ranked_moments[:max_clips], start=1):
        print(f"\nCreating Short {index}...")

        raw_path = job_dir / f"short-{index}-raw.mp4"
        final_path = job_dir / f"short-{index}-vertical.mp4"

        print("Creating video clip...")
        create_clip(
            video_path,
            moment["start"],
            moment["end"],
            str(raw_path)
        )

        print("Converting to V5 vertical format...")
        convert_to_vertical(str(raw_path), str(final_path))

        created_clips.append({
            "path": str(final_path),
            "score": moment["score"],
            "start": moment["start"],
            "end": moment["end"],
            "text": moment["text"]
        })

        print("Created:", final_path)

    print("\n===== PIPELINE COMPLETED =====")
    return created_clips
