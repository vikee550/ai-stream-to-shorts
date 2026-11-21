from pathlib import Path
import subprocess


def get_video_duration(video_path: str) -> float:
    """Get video duration using FFprobe."""

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Could not read video duration: {result.stderr[-1000:]}"
        )

    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Invalid video duration.")


def extract_frame(
    video_path: str,
    timestamp: float,
    output_path: str
) -> str:
    """Safely extract one frame from a video."""

    video = Path(video_path)
    output = Path(output_path)

    if not video.is_file():
        raise FileNotFoundError(
            f"Video file not found: {video_path}"
        )

    if timestamp < 0:
        raise ValueError("Timestamp cannot be negative.")

    duration = get_video_duration(str(video))

    if timestamp >= duration:
        raise ValueError(
            f"Timestamp {timestamp} exceeds video duration {duration:.2f} seconds."
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(timestamp),
        "-i", str(video),
        "-frames:v", "1",
        "-update", "1",
        str(output)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg frame extraction failed: {result.stderr[-1000:]}"
        )

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Extracted frame is missing or empty.")

    return str(output)
