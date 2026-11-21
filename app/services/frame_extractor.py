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


def extract_multiple_frames(
    video_path: str,
    timestamp: float,
    output_dir: str = "storage/temp",
    frame_count: int = 3,
    interval: float = 1.0
) -> list:
    """Extract consecutive frames around a selected timestamp."""

    if frame_count < 1:
        raise ValueError("frame_count must be at least 1.")

    if interval <= 0:
        raise ValueError("interval must be greater than 0.")

    duration = get_video_duration(video_path)

    if timestamp < 0 or timestamp >= duration:
        raise ValueError("Timestamp is outside video duration.")

    video = Path(video_path)
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    paths = []
    first_offset = (frame_count - 1) / 2

    for index in range(frame_count):
        frame_timestamp = (
            timestamp + (index - first_offset) * interval
        )

        frame_timestamp = max(0, min(frame_timestamp, duration - 0.01))

        output_path = directory / (
            f"sequence-{int(timestamp)}-{index}.jpg"
        )

        extract_frame(
            str(video),
            frame_timestamp,
            str(output_path)
        )

        paths.append(str(output_path))

    return paths
