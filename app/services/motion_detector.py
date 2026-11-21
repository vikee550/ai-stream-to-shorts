import cv2
import numpy as np


def analyze_motion(
    video_path: str,
    start: float,
    end: float,
    sample_interval: float = 0.5
) -> dict:
    """Measure visual changes between consecutive video frames."""

    if start < 0 or end <= start:
        raise ValueError("Invalid video time range.")

    if sample_interval <= 0:
        raise ValueError("sample_interval must be greater than 0.")

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    duration = capture.get(cv2.CAP_PROP_FRAME_COUNT) / fps if fps > 0 else 0

    if start >= duration or end > duration:
        capture.release()
        raise ValueError("Requested time range exceeds video duration.")

    differences = []
    previous = None
    timestamp = start

    try:
        while timestamp <= end:
            capture.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            success, frame = capture.read()

            if not success:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 180))

            if previous is not None:
                difference = cv2.absdiff(previous, gray)
                motion_ratio = float(np.mean(difference > 20))
                differences.append(motion_ratio)

            previous = gray
            timestamp += sample_interval

    finally:
        capture.release()

    if not differences:
        return {
            "motion_score": 0,
            "motion_ratio": 0,
            "samples_compared": 0
        }

    average_motion = float(np.mean(differences))

    return {
        "motion_score": round(min(100, average_motion * 200), 2),
        "motion_ratio": round(average_motion, 4),
        "samples_compared": len(differences)
    }
