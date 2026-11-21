import re


ACTION_SCORES = {
    "extreme": {
        "score": 95,
        "keywords": [
            "explosion", "massive explosion",
            "major crash", "dramatic destruction"
        ]
    },
    "high": {
        "score": 80,
        "keywords": [
            "shooting", "gunfight", "firefight",
            "intense fight", "combat", "battle",
            "chasing", "high speed chase"
        ]
    },
    "medium": {
        "score": 55,
        "keywords": [
            "running", "jumping", "escaping",
            "crashing", "falling", "vehicle collision"
        ]
    },
    "low": {
        "score": 20,
        "keywords": [
            "walking", "interacting",
            "gesturing", "character interaction"
        ]
    },
    "normal": {
        "score": 5,
        "keywords": [
            "talking", "standing",
            "conversation", "sitting"
        ]
    }
}


def calculate_visual_score(action: str) -> dict:
    """Calculate a rule-based score from the described visible action."""

    text = re.sub(r"\s+", " ", str(action).lower()).strip()

    if not text or text in {
        "visible action", "unknown", "none"
    }:
        return {
            "visual_score": 0,
            "action_category": "unknown",
            "matched_action": None
        }

    for category, data in ACTION_SCORES.items():
        for keyword in data["keywords"]:
            if re.search(
                r"\b" + re.escape(keyword) + r"\b",
                text
            ):
                return {
                    "visual_score": data["score"],
                    "action_category": category,
                    "matched_action": keyword
                }

    return {
        "visual_score": 0,
        "action_category": "unclassified",
        "matched_action": None
    }
