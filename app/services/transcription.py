from functools import lru_cache
from pathlib import Path

from faster_whisper import WhisperModel


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load Whisper model only once."""

    print("Loading Whisper model...")

    model = WhisperModel(
        "small",
        device="cuda",
        compute_type="float16"
    )

    print("Whisper model ready!")

    return model


def transcribe_audio(audio_path: str) -> dict:
    """Transcribe an audio file and return text with timestamps."""

    audio_file = Path(audio_path)

    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = get_whisper_model()

    print(f"Transcribing: {audio_file.name}")

    segments, info = model.transcribe(
        str(audio_file),
        beam_size=5
    )

    results = []

    for segment in segments:
        results.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })

    full_text = " ".join(item["text"] for item in results)

    return {
        "language": info.language,
        "language_probability": info.language_probability,
        "full_text": full_text,
        "segments": results
    }