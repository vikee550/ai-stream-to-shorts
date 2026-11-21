
from faster_whisper import WhisperModel


def main():
    print("Loading Whisper model...")

    model = WhisperModel(
        "small",
        device="cuda",
        compute_type="float16"
    )

    print("Transcribing audio...")

    segments, info = model.transcribe(
        "storage/temp/sample-speech.wav",
        beam_size=5
    )

    print("\nDetected language:", info.language)
    print("\nTranscription:\n")

    for segment in segments:
        print(
            f"[{segment.start:.2f}s - {segment.end:.2f}s] "
            f"{segment.text}"
        )


if __name__ == "__main__":
    main()
