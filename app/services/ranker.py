import logging
import json
import ollama


logger = logging.getLogger(__name__)

MODEL_NAME = "llama3.2:3b"
BATCH_SIZE = 2


def analyze_batch(moments):
    """Analyze moments using transcript and pre-filter signals."""

    prompt_data = [
        {
            "index": index,
            "duration": moment["duration"],
            "text": moment["text"],
            "pre_score": moment.get("pre_score", 0),
            "keyword_hits": moment.get("keyword_hits", 0),
            "reaction_hits": moment.get("reaction_hits", 0),
            "excitement": moment.get("excitement", 0)
        }
        for index, moment in enumerate(moments)
    ]

    prompt = f"""
You are an expert YouTube Shorts editor.

Analyze every video moment independently.

Give each moment a score from 0 to 100.

Scoring boundaries:
- 0-20: Boring or ordinary content with little engagement.
- 21-40: Slightly interesting but weak highlight potential.
- 41-60: Moderately engaging conversation or activity.
- 61-80: Strong reactions, humor, exciting action or surprising events.
- 81-100: Exceptional highlight with clear, memorable engagement.

A normal conversation without a strong reaction or interesting event
should generally score between 20 and 45.

Consider:
- Genuine excitement and emotion
- Humor and natural reactions
- Surprising or interesting events
- Interesting conversation
- Potential viewer engagement
- Transcript clarity and context

Pre-filter signals are supporting evidence only.
Do not give a high score just because keyword counts are high.

Important:
- Analyze every moment independently.
- Do not invent events.
- Do not assume something happened if the transcript is unclear.
- Ordinary conversation should not automatically receive a high score.
- Return valid JSON only.

Required format:
{{
  "ranked_moments": [
    {{
      "index": 0,
      "score": 75,
      "reasons": ["Interesting reaction"]
    }}
  ]
}}

Moments:
{json.dumps(prompt_data, ensure_ascii=False)}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"temperature": 0}
    )

    data = json.loads(response["message"]["content"])

    results = {}

    for item in data.get("ranked_moments", []):
        index = item.get("index")
        score = item.get("score")

        if (
            isinstance(index, int)
            and not isinstance(index, bool)
            and 0 <= index < len(moments)
            and isinstance(score, (int, float))
        ):
            results[index] = {
                "score": max(0, min(100, round(score))),
                "reasons": item.get("reasons", [])
            }

    return results


def rank_moments(moments):
    """Rank moments with batch retries and safe failure handling."""

    if not moments:
        return []

    print("\nAnalyzing moments with local AI...")

    ranked = []

    for batch_start in range(0, len(moments), BATCH_SIZE):
        batch = moments[batch_start:batch_start + BATCH_SIZE]

        print(
            f"Analyzing moments "
            f"{batch_start + 1} to {batch_start + len(batch)} "
            f"of {len(moments)}..."
        )

        try:
            results = analyze_batch(batch)
        except Exception:
            logger.exception("Batch ranking failed.")
            results = {}

        for index, moment in enumerate(batch):
            result = results.get(index)
            ranking_status = "ai"

            if result is None:
                print(f"Retrying moment {batch_start + index + 1} individually...")

                try:
                    retry_results = analyze_batch([moment])
                    result = retry_results.get(0)
                except Exception:
                    logger.exception("Individual ranking failed.")

                if result is None:
                    ranking_status = "fallback"
                    result = {
                        "score": 0,
                        "reasons": [
                            "AI ranking unavailable; candidate not scored."
                        ]
                    }

            ranked.append({
                **moment,
                "score": result["score"],
                "reasons": result["reasons"],
                "ranking_status": ranking_status
            })

    return sorted(
        ranked,
        key=lambda item: item["score"],
        reverse=True
    )
