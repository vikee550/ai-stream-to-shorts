from pathlib import Path

from app.services.video import extract_audio, get_video_info
from app.services.transcription import transcribe_audio


def process_video(video_path: str) -> dict:
    """Extract audio from a video and transcribe it."""

    video_file = Path(video_path)

    if not video_file.is_file():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    print("Step 1: Reading video information...")

    video_info = get_video_info(str(video_file))

    print("Video duration:", video_info["duration"], "seconds")

    audio_path = (
        Path("storage/temp")
        / f"{video_file.stem}-audio.wav"
    )

    print("\nStep 2: Extracting audio...")

    extract_audio(str(video_file), str(audio_path))

    print("Audio extracted:", audio_path)

    print("\nStep 3: Transcribing audio with Whisper...")

    transcription = transcribe_audio(str(audio_path))

    print("\nTranscription completed!")

    return {
        "video": video_info,
        "transcription": transcription
    }
