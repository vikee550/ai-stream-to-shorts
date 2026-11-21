import re


ACTION_SCORES = {
    "extreme": {
        "score": 95,
        "keywords": [
            "massive explosion",
            "dramatic destruction",
            "explosion",
            "explodes",
            "exploding",
            "major crash"
        ]
    },
    "vehicle_high": {
        "score": 85,
        "keywords": [
            "high speed chase",
            "vehicle crash",
            "car crash",
            "vehicle collision",
            "car collision",
            "crashing into a vehicle",
            "vehicle explosion"
        ]
    },
    "high": {
        "score": 80,
        "keywords": [
            "intense fight",
            "gunfight",
            "firefight",
            "shooting",
            "combat",
            "battle",
            "chasing"
        ]
    },
    "vehicle_medium": {
        "score": 70,
        "keywords": [
            "drifting",
            "doing a drift",
            "high speed driving",
            "driving at high speed",
            "racing"
        ]
    },
    "medium": {
        "score": 55,
        "keywords": [
            "escaping",
            "crashing",
            "jumping",
            "falling",
            "running"
        ]
    },
    "vehicle_low": {
        "score": 20,
        "keywords": [
            "normal driving",
            "driving a car",
            "driving a vehicle",
            "riding a motorcycle"
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
    """Calculate visual score with vehicle and action intelligence."""

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

        clauses = re.split(
            r"\b(?:but|however|although|yet)\b|[.;!?]",
            preceding_text
        )

        if NEGATION_PATTERN.search(clauses[-1]):
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
