
import json
import subprocess
from pathlib import Path


def get_video_info(video_path: str) -> dict:
    """Extract video metadata using FFprobe."""

    video_file = Path(video_path)

    if not video_file.is_file():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    command = [
        "ffprobe",
        "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        str(video_file)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    data = json.loads(result.stdout)

    video_stream = next(
        (
            stream for stream in data["streams"]
            if stream["codec_type"] == "video"
        ),
        None
    )

    if video_stream is None:
        raise ValueError("No video stream found.")

    return {
        "filename": video_file.name,
        "duration": float(data["format"]["duration"]),
        "width": video_stream["width"],
        "height": video_stream["height"],
        "fps": video_stream.get("r_frame_rate"),
        "codec": video_stream.get("codec_name"),
        "format": data["format"].get("format_name")
    }


def extract_audio(video_path: str, output_path: str) -> str:
    """Extract audio from a video and save it as WAV."""

    video_file = Path(video_path)
    audio_file = Path(output_path)

    if not video_file.is_file():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    audio_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i", str(video_file),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio_file)
    ]

    subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return str(audio_file)
