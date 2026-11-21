import array
import math
import subprocess
from pathlib import Path


def analyze_audio(
    video_path: str,
    start: float,
    end: float,
    sample_interval: float = 0.5
) -> dict:
    """Analyze audio loudness, spikes and quiet sections."""

    if not isinstance(video_path, (str, Path)):
        raise TypeError("video_path must be a string or Path.")

    for name, value in {
        "start": start,
        "end": end,
        "sample_interval": sample_interval
    }.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number.")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite.")

    if start < 0 or end <= start:
        raise ValueError("Invalid audio time range.")

    if sample_interval <= 0:
        raise ValueError("sample_interval must be positive.")

    sample_rate = 8000
    window_size = max(1, round(sample_rate * sample_interval))

    if not Path(video_path).is_file():
        raise FileNotFoundError(video_path)

    command = [
        "ffmpeg",
        "-v", "error",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(end - start),
        "-vn",
        "-ac", "1",
        "-ar", str(sample_rate),
        "-f", "f32le",
        "pipe:1"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        check=True,
        timeout=120
    )

    raw_audio = result.stdout
    sample_count = len(raw_audio) // 4

    if sample_count == 0:
        raise RuntimeError("No audio samples extracted.")

    samples = array.array("f")
    samples.frombytes(raw_audio[:sample_count * 4])

    energies = []

    for index in range(0, len(samples), window_size):
        chunk = samples[index:index + window_size]

        rms = math.sqrt(
            sum(value * value for value in chunk) / len(chunk)
        )

        db = 20 * math.log10(max(rms, 1e-8))
        energies.append(db)

    average_db = sum(energies) / len(energies)
    peak_db = max(energies)

    spike_threshold = average_db + 6
    quiet_threshold = average_db - 10

    spikes = []
    quiet_sections = []

    for index, value in enumerate(energies):
        timestamp = round(start + index * sample_interval, 2)

        if value > spike_threshold:
            spikes.append(timestamp)

        if value < quiet_threshold:
            quiet_sections.append({
                "start": timestamp,
                "end": round(
                    min(start + (index + 1) * sample_interval, end),
                    2
                ),
                "loudness_db": round(value, 2)
            })

    return {
        "average_loudness_db": round(average_db, 2),
        "peak_loudness_db": round(peak_db, 2),
        "spike_count": len(spikes),
        "spike_timestamps": spikes,
        "quiet_section_count": len(quiet_sections),
        "quiet_sections": quiet_sections,
        "samples_analyzed": len(energies)
    }
