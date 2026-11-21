from app.services.frame_extractor import extract_frame
from app.services.visual_analyzer import analyze_frame


def analyze_video_moment(
    video_path: str,
    timestamp: float
) -> dict:
    """Extract and visually analyze a selected video moment."""

    frame_path = (
        f"storage/temp/visual-frame-{int(timestamp)}.jpg"
    )

    print(f"Extracting frame at {timestamp} seconds...")

    extract_frame(
        video_path,
        timestamp,
        frame_path
    )

    print("Analyzing frame with LLaVA...")

    result = analyze_frame(frame_path)

    return {
        "timestamp": timestamp,
        "frame_path": frame_path,
        "visual_analysis": result
    }
