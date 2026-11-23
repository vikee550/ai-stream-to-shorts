import logging
import shutil
import uuid

from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.shorts_pipeline import create_shorts


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Stream to Shorts",
    description="AI-powered YouTube stream clipping application",
    version="0.3.0"
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
CLIPS_DIR = STORAGE_DIR / "clips"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"
}

ALLOWED_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be"
}


class YouTubeURLRequest(BaseModel):
    url: str
    max_clips: int = Field(default=3, ge=1, le=10)


def generate_shorts(video_path: Path, job_id: str, max_clips: int):
    job_output_dir = CLIPS_DIR / job_id
    job_output_dir.mkdir(parents=True, exist_ok=True)

    clips = create_shorts(
        video_path=str(video_path),
        max_clips=max_clips,
        output_dir=str(job_output_dir)
    )

    results = []

    for clip in clips:
        clip_path = Path(clip["path"])
        relative_path = clip_path.relative_to(CLIPS_DIR)

        results.append({
            **clip,
            "url": f"/clips/{relative_path.as_posix()}"
        })

    return {
        "job_id": job_id,
        "status": "completed",
        "total_clips": len(results),
        "clips": results
    }


def download_youtube_video(url: str, destination: Path) -> Path:
    parsed = urlparse(url)

    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in ALLOWED_YOUTUBE_HOSTS
        or parsed.username
        or parsed.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid YouTube video URL."
        )

    options = {
        "format": "bestvideo*+bestaudio/best",
        "outtmpl": str(destination / "source.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 3
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.extract_info(url, download=True)

    video_extensions = {".mp4", ".mkv", ".webm", ".mov"}
    downloaded_files = [
        path for path in destination.glob("source.*")
        if path.suffix.lower() in video_extensions
        and path.is_file()
        and path.stat().st_size > 0
    ]

    if not downloaded_files:
        raise RuntimeError("Downloaded video file was not found.")

    return downloaded_files[0]


@app.get("/")
def home():
    return {
        "message": "AI Stream to Shorts is running!",
        "status": "success"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload")
def upload_video(
    file: UploadFile = File(...),
    max_clips: int = 3
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format."
        )

    if not 1 <= max_clips <= 10:
        raise HTTPException(
            status_code=400,
            detail="max_clips must be between 1 and 10."
        )

    job_id = uuid.uuid4().hex
    job_upload_dir = UPLOAD_DIR / job_id
    job_upload_dir.mkdir(parents=True, exist_ok=True)

    video_path = job_upload_dir / f"input{extension}"

    try:
        with video_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

        logger.info("Processing uploaded video: %s", job_id)

        return generate_shorts(video_path, job_id, max_clips)

    except Exception:
        logger.exception("Upload processing failed: %s", job_id)
        raise HTTPException(
            status_code=500,
            detail="Video processing failed. Check application logs."
        )

    finally:
        file.file.close()


@app.post("/process-url")
def process_youtube_url(request: YouTubeURLRequest):
    job_id = uuid.uuid4().hex

    job_upload_dir = UPLOAD_DIR / job_id
    job_upload_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info("Downloading YouTube video: %s", job_id)

        video_path = download_youtube_video(
            request.url,
            job_upload_dir
        )

        logger.info("Starting Shorts pipeline: %s", job_id)

        return generate_shorts(
            video_path,
            job_id,
            request.max_clips
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("YouTube processing failed: %s", job_id)

        raise HTTPException(
            status_code=502,
            detail="YouTube download or video processing failed. Check application logs."
        )


app.mount(
    "/clips",
    StaticFiles(directory=str(CLIPS_DIR)),
    name="clips"
)
