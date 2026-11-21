from pathlib import Path
import yt_dlp


def fetch_captions(url: str, languages=None) -> dict:
    languages = languages or ["en"]

    output_dir = Path("storage/temp")
    output_dir.mkdir(parents=True, exist_ok=True)

    options = {
        "skip_download": True,
        "writesubtitles": False,
        "writeautomaticsub": True,
        "subtitleslangs": languages,
        "subtitlesformat": "vtt/best",
        "outtmpl": str(output_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "sleep_interval": 5,
        "max_sleep_interval": 10,
        "ignoreerrors": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as error:
        return {"files": [], "count": 0, "error": str(error)}

    files = list(output_dir.glob("*.vtt"))

    return {
        "files": [str(file) for file in files],
        "count": len(files),
    }
