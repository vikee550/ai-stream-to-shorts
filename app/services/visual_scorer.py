import re


ACTION_SCORES = {
    "extreme": {
        "score": 95,
        "keywords": [
            "massive explosion",
            "dramatic destruction",
            "explosion",
            "major crash"
        ]
    },
    "high": {
        "score": 80,
        "keywords": [
            "high speed chase",
            "intense fight",
            "gunfight",
            "firefight",
            "shooting",
            "combat",
            "battle",
            "chasing"
        ]
    },
    "medium": {
        "score": 55,
        "keywords": [
            "vehicle collision",
            "escaping",
            "crashing",
            "jumping",
            "falling",
            "running"
        ]
    },
    "low": {
        "score": 20,
        "keywords": [
            "character interaction",
            "interacting",
            "gesturing",
            "walking"
        ]
    },
    "normal": {
        "score": 5,
        "keywords": [
            "talking",
            "standing",
            "conversation",
            "sitting"
        ]
    }
}


NEGATION_PATTERN = re.compile(
    r"\b(no|not|never|without|isn't|wasn't|weren't|"
    r"didn't|doesn't|don't|cannot|can't)\b",
    re.IGNORECASE
)


def calculate_visual_score(action: str) -> dict:
    """Calculate visual score with action-specific negation handling."""

    text = re.sub(r"\s+", " ", str(action).lower()).strip()

    if not text or text in {"visible action", "unknown", "none"}:
        return {
            "visual_score": 0,
            "action_category": "unknown",
            "matched_action": None
        }

    matches = []

    for category, data in ACTION_SCORES.items():
        for keyword in data["keywords"]:
            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            for match in re.finditer(pattern, text):
                matches.append({
                    "category": category,
                    "score": data["score"],
                    "keyword": keyword,
                    "start": match.start()
                })

    if not matches:
        return {
            "visual_score": 0,
            "action_category": "unclassified",
            "matched_action": None
        }

    valid_matches = []

    for item in matches:
        preceding_text = text[:item["start"]]

        # Contrast words reset the scope of earlier negations.
        clauses = re.split(
            r"\b(?:but|however|although|yet)\b|[.;!?]",
            preceding_text
        )

        current_clause = clauses[-1]

        if NEGATION_PATTERN.search(current_clause):
            continue

        valid_matches.append(item)

    if not valid_matches:
        return {
            "visual_score": 0,
            "action_category": "negated",
            "matched_action": matches[0]["keyword"]
        }

    best = max(valid_matches, key=lambda item: item["score"])

    return {
        "visual_score": best["score"],
        "action_category": best["category"],
        "matched_action": best["keyword"]
    }
