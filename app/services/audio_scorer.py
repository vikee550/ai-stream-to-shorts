def calculate_audio_score(audio_data: dict) -> dict:
    """Calculate a provisional audio activity score."""

    if not isinstance(audio_data, dict):
        raise TypeError("audio_data must be a dictionary.")

    spike_count = audio_data.get("spike_count", 0)
    quiet_count = audio_data.get("quiet_section_count", 0)
    samples = audio_data.get("samples_analyzed", 0)

    values = {
        "spike_count": spike_count,
        "quiet_section_count": quiet_count,
        "samples_analyzed": samples
    }

    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer.")
        if value < 0:
            raise ValueError(f"{name} cannot be negative.")

    if spike_count > samples or quiet_count > samples:
        raise ValueError("Activity counts cannot exceed total samples.")

    if samples == 0:
        return {
            "audio_score": 0,
            "spike_ratio": 0,
            "quiet_ratio": 0
        }

    spike_ratio = spike_count / samples
    quiet_ratio = quiet_count / samples

    activity_score = min(100, spike_ratio * 500)
    quiet_penalty = min(30, quiet_ratio * 100)

    audio_score = max(0, min(100, round(
        activity_score - quiet_penalty + 20
    )))

    return {
        "audio_score": audio_score,
        "spike_ratio": round(spike_ratio, 3),
        "quiet_ratio": round(quiet_ratio, 3)
    }
