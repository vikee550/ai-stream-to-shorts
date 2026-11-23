# AI Stream to Shorts 🎬

An AI-powered video clipping application built with Python and FastAPI.

Convert long videos into short vertical videos using AI-based moment detection, ranking and automatic video processing.

## Features

- YouTube video downloading with yt-dlp
- Audio transcription with Faster-Whisper
- AI-based moment detection and ranking
- Video processing with FFmpeg
- Automatic vertical video conversion
- Original audio preservation
- FastAPI endpoints for uploading and processing videos
- MP4 video delivery through API

## Video Specifications

| Property | Output |
|---|---|
| Resolution | 1080 × 1920 |
| Aspect ratio | 9:16 |
| Video codec | H.264 |
| Audio codec | AAC |
| Layout | Gameplay above, facecam below |
| Subtitles | Disabled |

## Technology Stack

- Python
- FastAPI
- Ollama
- Google GenAI
- Faster-Whisper
- OpenCV
- FFmpeg
- yt-dlp

## Ubuntu Installation

Install system dependencies:

```bash
sudo apt update
sudo apt install ffmpeg python3-venv python3-pip
