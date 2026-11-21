from pathlib import Path

from app.services.pipeline import process_video
from app.services.moment_detector import detect_moments
from app.services.ranker import rank_moments
from app.services.clip_generator import create_clip
from app.services.vertical_converter import convert_to_vertical
from app.services.caption_generator import create_srt
from app.services.subtitle_burner import burn_subtitles


def create_shorts(video_path: str, max_clips: int = 3) -> list:
    """Automatically create ranked vertical shorts with captions."""

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

    output_dir = Path("storage/clips")
    output_dir.mkdir(parents=True, exist_ok=True)

    created_clips = []

    print("\nStep 4: Generating vertical shorts with captions...")

    for index, moment in enumerate(
        ranked_moments[:max_clips], start=1
    ):
        print(f"\nCreating Short {index}...")

        start = moment["start"]
        end = moment["end"]

        raw_path = output_dir / f"short-{index}-raw.mp4"
        vertical_path = output_dir / f"short-{index}-vertical-uncaptioned.mp4"
        subtitle_path = output_dir / f"short-{index}.srt"
        final_path = output_dir / f"short-{index}-vertical.mp4"

        print("Creating video clip...")
        create_clip(
            video_path,
            start,
            end,
            str(raw_path)
        )

        print("Converting to vertical format...")
        convert_to_vertical(
            str(raw_path),
            str(vertical_path)
        )

        print("Preparing subtitles...")

        clip_segments = []

        for segment in transcription["segments"]:
            segment_start = max(segment["start"], start)
            segment_end = min(segment["end"], end)

            if segment_end > segment_start:
                clip_segments.append({
                    "start": round(segment_start - start, 2),
                    "end": round(segment_end - start, 2),
                    "text": segment["text"]
                })

        create_srt(
            clip_segments,
            str(subtitle_path)
        )

        if clip_segments:
            print("Burning captions into video...")
            burn_subtitles(
                str(vertical_path),
                str(subtitle_path),
                str(final_path)
            )
        else:
            print("No subtitles found. Keeping video without captions.")
            final_path = vertical_path

        clip_info = {
            "path": str(final_path),
            "score": moment["score"],
            "start": start,
            "end": end,
            "text": moment["text"]
        }

        created_clips.append(clip_info)

        print("Created:", final_path)
        print("Score:", moment["score"])

    print("\n===== PIPELINE COMPLETED =====")

    return created_clips
