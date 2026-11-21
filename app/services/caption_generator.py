from pathlib import Path


def create_srt(segments: list, output_path: str) -> str:
    """Create an SRT subtitle file from Whisper segments."""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    def format_time(seconds: float) -> str:
        milliseconds = round(seconds * 1000)

        hours = milliseconds // 3600000
        milliseconds %= 3600000

        minutes = milliseconds // 60000
        milliseconds %= 60000

        secs = milliseconds // 1000
        milliseconds %= 1000

        return (
            f"{hours:02}:"
            f"{minutes:02}:"
            f"{secs:02},"
            f"{milliseconds:03}"
        )

    with output_file.open("w", encoding="utf-8") as file:
        for index, segment in enumerate(segments, start=1):
            start = format_time(segment["start"])
            end = format_time(segment["end"])
            text = segment["text"].strip()

            file.write(f"{index}\n")
            file.write(f"{start} --> {end}\n")
            file.write(f"{text}\n\n")

    return str(output_file)
