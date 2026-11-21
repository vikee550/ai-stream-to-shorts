
import subprocess
from pathlib import Path


def create_clip(
    video_path: str,
    start: float,
    end: float,
    output_path: str
) -> str:
    """Create a video clip from the selected time range."""

    video_file = Path(video_path)
    output_file = Path(output_path)

    if not video_file.is_file():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    if start < 0 or end <= start:
        raise ValueError("Invalid clip timestamps.")

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", str(video_file),
        "-t", str(end - start),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(output_file)
    ]

    subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return str(output_file)
