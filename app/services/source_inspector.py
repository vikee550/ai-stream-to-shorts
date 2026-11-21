from urllib.parse import urlparse

import yt_dlp


ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtube-nocookie.com",
}


def inspect_youtube_source(url: str) -> dict:
    """Inspect YouTube metadata, captions and available formats."""

    parsed = urlparse(url.strip())

    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in ALLOWED_HOSTS
    ):
        raise ValueError("Please provide a valid YouTube URL.")

    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        raise RuntimeError("Could not inspect YouTube source.")

    formats = []

    for item in info.get("formats", []):
        formats.append({
            "format_id": item.get("format_id"),
            "ext": item.get("ext"),
            "protocol": item.get("protocol"),
            "width": item.get("width"),
            "height": item.get("height"),
            "vcodec": item.get("vcodec"),
            "acodec": item.get("acodec"),
        })

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "duration": info.get("duration"),
        "is_live": info.get("is_live"),
        "live_status": info.get("live_status"),
        "manual_captions": list(info.get("subtitles", {}).keys()),
        "automatic_captions": list(
            info.get("automatic_captions", {}).keys()
        ),
        "formats": formats,
    }
