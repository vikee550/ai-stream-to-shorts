from pathlib import Path
import subprocess


def extract_frame(
    video_path: str,
    timestamp: float,
    output_path: str
) -> str:
    """Extract one frame from a video at a given timestamp."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-ss", str(timestamp),
        "-i", video_path,
        "-frames:v", "1",
        "-update", "1",
        str(output)
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if not output.is_file():
        raise RuntimeError("Frame extraction failed.")

    return str(output)
