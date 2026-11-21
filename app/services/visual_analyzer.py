import json
import ollama

from app.services.visual_scorer import calculate_visual_score


MODEL_NAME = "llava:7b"


def analyze_frame(image_path: str) -> dict:
    """Analyze gaming footage and calculate evidence-based visual scores."""

    prompt = """
You are an expert gaming footage analyst.

Analyze this single video frame for visible gameplay evidence.

Return valid JSON with exactly these fields:
{
  "scene": "brief description of the visible scene",
  "scene_type": "gameplay",
  "people_visible": false,
  "action": "specific visible action",
  "reaction": "visible human emotion or none",
  "reason": "visual evidence supporting the action"
}

Allowed scene_type values:
- gameplay
- cutscene
- facecam
- other

ACTION DETECTION:

Carefully inspect the frame for:

1. Combat:
   - Shooting or firing a weapon
   - Aiming at an opponent
   - Fighting or attacking
   - Explosions or visible destruction

2. Vehicle activity:
   - Driving or riding
   - Racing or drifting
   - High-speed chase
   - Collision or crash

3. Character movement:
   - Running, jumping, falling
   - Escaping or chasing
   - Walking or standing

4. Other activities:
   - Interacting with objects
   - Talking or performing
   - Exploring or navigating

IMPORTANT RULES:

- Describe only what is visually supported by this frame.
- A visible weapon does NOT automatically mean shooting.
- Aiming does NOT automatically mean firing.
- A vehicle does NOT automatically mean racing.
- Do not infer motion from a single still image.
- Do not invent explosions, collisions, enemies or reactions.
- If the action is unclear, explicitly say "unclear".
- Distinguish real people in facecam from in-game characters.
- Do not treat in-game characters as real people.
- Do not generate scores or excitement ratings.
- Keep descriptions specific and concise.
- Return valid JSON only.
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
