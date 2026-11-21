import json
import ollama

from app.services.visual_scorer import calculate_visual_score


MODEL_NAME = "llava:7b"


def analyze_frame(image_path: str) -> dict:
    """Analyze a frame and calculate evidence-based visual scores."""

    prompt = """
You are a visual analyst for gaming YouTube Shorts.

Describe ONLY what is clearly visible in this image.

Return valid JSON:
{
  "scene": "specific scene description",
  "scene_type": "gameplay",
  "people_visible": false,
  "action": "specific visible action",
  "reaction": "visible emotion or none",
  "reason": "brief visual evidence"
}

Scene types:
- gameplay
- cutscene
- facecam
- other

Rules:
- Describe actual visible characters and actions.
- Do not invent events.
- In-game characters are not real people.
- people_visible means real people, such as a streamer facecam.
- If characters are talking, describe their conversation.
- If uncertain, say so.
- Do not generate excitement or Shorts scores.
- Return JSON only.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [image_path]
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

    result["people_visible"] = bool(result.get("people_visible", False))

    return result
