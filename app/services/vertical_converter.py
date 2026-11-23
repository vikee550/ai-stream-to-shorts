import subprocess
from pathlib import Path


def convert_to_vertical(
    input_path: str,
    output_path: str
) -> str:
    """Create vertical Shorts with gameplay above facecam."""

    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.is_file():
        raise FileNotFoundError(f"Video not found: {input_path}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    filter_complex = (
        "[0:v]crop=868:1080:300:0,"
        "scale=1080:1344[top];"
        "[0:v]crop=990:528:0:552,"
        "scale=1080:576[face];"
        "[top][face]vstack=inputs=2[v]"
    )

    command = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a?",
        "-r", "60",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "128k",
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
