from app.services.transcription import transcribe_audio


def main():
    audio_path = "storage/temp/sample-speech.wav"

    print("Testing transcription service...\n")

    result = transcribe_audio(audio_path)

    print("\nLanguage:", result["language"])
    print("Language confidence:", result["language_probability"])

    print("\nFull transcription:")
    print(result["full_text"])

    print("\nTimestamped segments:")

    for segment in result["segments"]:
        print(
            f"[{segment['start']}s - {segment['end']}s] "
            f"{segment['text']}"
        )


if __name__ == "__main__":
    main()