
import subprocess
from pathlib import Path


def convert_to_vertical(
    input_path: str,
    output_path: str
) -> str:
    """Convert a video to vertical 9:16 format."""

    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.is_file():
        raise FileNotFoundError(
            f"Video not found: {input_path}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",
        "-i", str(input_file),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920",
        "-c:v", "libx264",
        "-preset", "fast",
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
