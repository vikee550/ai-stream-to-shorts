import subprocess
from pathlib import Path


def burn_subtitles(
    video_path: str,
    subtitle_path: str,
    output_path: str
) -> str:
    """Burn subtitles permanently into a video."""

    video_file = Path(video_path)
    subtitle_file = Path(subtitle_path)
    output_file = Path(output_path)

    if not video_file.is_file():
        raise FileNotFoundError(f"Video not found: {video_path}")

    if not subtitle_file.is_file():
        raise FileNotFoundError(f"Subtitle not found: {subtitle_path}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i", str(video_file),
        "-vf", f"subtitles={subtitle_file}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "copy",
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
