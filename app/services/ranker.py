import math
import logging
import json
import ollama


logger = logging.getLogger(__name__)

MODEL_NAME = "llama3.2:3b"
BATCH_SIZE = 6


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
You are an expert YouTube Shorts editor specializing in gaming highlights.

Analyze every video moment independently and assign a meaningful score from 0 to 100.

Evaluate these four dimensions:
1. Action: What actually happens in the moment?
2. Tension: How intense, risky, or suspenseful is it?
3. Payoff: How significant or satisfying is the outcome?
4. Reaction: How genuine and engaging is the player's reaction?

FACTOR SCORING:

Give each factor an independent score from 0 to 100:

- action: Quality and impressiveness of the actual gameplay event.
- tension: Risk, suspense, difficulty, and intensity.
- payoff: Significance and satisfaction of the event outcome.
- reaction: Genuine emotion, humor, and audience engagement.

Guidelines:
- Routine looting and movement should score low in action and payoff.
- A close escape can score high in tension even without a kill.
- A confirmed squad wipe can score high in action and payoff.
- Do not assume an achievement without transcript evidence.
- Compare moments within the same batch before assigning scores.
- Give stronger events higher scores than weaker events.
- Do not copy the same score breakdown across different events.
- Use the full scoring range when the evidence supports it.
- Do not give identical factor scores automatically.
- Judge the actual event, not just exciting words.
- Return valid JSON only.

Required format:
{{
  "ranked_moments": [
    {{
      "index": 0,
      "action": 80,
      "tension": 70,
      "payoff": 90,
      "reaction": 75,
      "reasons": ["Impressive gameplay", "Strong payoff"]
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

    weights = {
        "action": 0.35,
        "tension": 0.25,
        "payoff": 0.25,
        "reaction": 0.15,
    }

    for item in data.get("ranked_moments", []):
        if not isinstance(item, dict):
            continue

        index = item.get("index")

        if (
            not isinstance(index, int)
            or isinstance(index, bool)
            or not 0 <= index < len(moments)
            or index in results
        ):
            continue

        breakdown = {}
        valid_scores = True

        for factor in weights:
            value = item.get(factor)

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                valid_scores = False
                break

            breakdown[factor] = max(0, min(100, round(value)))

        if not valid_scores:
            logger.warning("Skipping invalid factor scores for moment %s.", index)
            continue

        final_score = round(
            sum(breakdown[factor] * weight for factor, weight in weights.items())
        )

        reasons = item.get("reasons", [])
        if not isinstance(reasons, list):
            reasons = []

        results[index] = {
            "score": final_score,
            "score_breakdown": breakdown,
            "reasons": [
                reason.strip()
                for reason in reasons
                if isinstance(reason, str) and reason.strip()
            ][:5],
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
                "score_breakdown": result.get("score_breakdown", {}),
                "reasons": result["reasons"],
                "ranking_status": ranking_status
            })

    return sorted(
        ranked,
        key=lambda item: item["score"],
        reverse=True
    )
