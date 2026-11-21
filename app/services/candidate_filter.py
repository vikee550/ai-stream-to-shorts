import re


HIGHLIGHT_PHRASES = {
    "wow", "omg", "insane", "crazy", "amazing",
    "unbelievable", "let's go", "no way", "finally",
    "clutch", "winner", "killed", "kill",
    "mission", "boss fight", "danger",
    "funny", "hilarious", "screaming",
    "incredible", "perfect"
}

REACTION_PHRASES = {
    "oh my god", "are you serious",
    "what happened", "no way",
    "let's go", "that's crazy"
}


def count_phrase_matches(text: str, phrases: set) -> int:
    count = 0

    for phrase in phrases:
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        if re.search(pattern, text):
            count += 1

    return count


def filter_candidates(windows: list, top_n: int = 30) -> list:
    """Pre-filter transcript windows using stronger text signals."""

    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    candidates = []

    for window in windows:
        text = str(window.get("text", "")).lower().strip()
        words = re.findall(r"\b[\w']+\b", text)

        if len(words) < 8:
            continue

        keyword_hits = count_phrase_matches(
            text, HIGHLIGHT_PHRASES
        )

        reaction_hits = count_phrase_matches(
            text, REACTION_PHRASES
        )

        excitement = min(text.count("!") + text.count("?"), 10)

        density = min(len(words) / 60, 2)

        score = (
            keyword_hits * 3
            + reaction_hits * 4
            + excitement
            + density
        )

        if keyword_hits == 0 and reaction_hits == 0 and excitement == 0:
            continue

        candidates.append({
            **window,
            "pre_score": round(score, 2),
            "keyword_hits": keyword_hits,
            "reaction_hits": reaction_hits,
            "excitement": excitement
        })

    return sorted(
        candidates,
        key=lambda item: item["pre_score"],
        reverse=True
    )[:top_n]
