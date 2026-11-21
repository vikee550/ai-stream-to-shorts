import json
import ollama

from app.services.visual_scorer import calculate_visual_score


MODEL_NAME = "llava:7b"


def analyze_frame_sequence(frame_paths: list) -> dict:
    """Analyze multiple consecutive frames to identify visible changes."""

    if not frame_paths or len(frame_paths) < 2:
        raise ValueError("At least 2 frames are required.")

    prompt = """
You are an expert gaming video analyst.

You will receive multiple consecutive frames from the same video.

Compare the frames in their given order.

Identify only actions and changes supported by visual evidence.

Return valid JSON:
{
  "scene": "brief scene description",
  "scene_type": "gameplay",
  "people_visible": false,
  "action": "specific action or unclear",
  "movement_detected": false,
  "scene_change_detected": false,
  "reaction": "visible emotion or none",
  "reason": "evidence from comparing the frames"
}

Analyze:
- Character movement between frames.
- Vehicle movement.
- Combat and visible weapon firing.
- Explosions and collisions.
- Changes in character positions.
- Camera movement and scene transitions.

Rules:
- Compare all frames in their supplied order.
- Distinguish actual object movement from camera movement.
- Do not assume a weapon is firing just because it is visible.
- Do not assume a vehicle is moving just because it appears in the frame.
- Do not invent events between frames.
- If movement or action cannot be established, say unclear.
- In-game characters are not real people.
- Return valid JSON only.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": frame_paths
        }],
        format="json",
        options={"temperature": 0}
    )

    result = json.loads(response["message"]["content"])

    scene_type = str(result.get("scene_type", "other")).lower()

    if scene_type not in {"gameplay", "cutscene", "facecam", "other"}:
        scene_type = "other"

    result["scene_type"] = scene_type
    result["gameplay_visible"] = scene_type in {"gameplay", "cutscene"}

    visual = calculate_visual_score(result.get("action", ""))

    result.update(visual)
    result["excitement"] = visual["visual_score"]
    result["shorts_potential"] = visual["visual_score"]

    return result
