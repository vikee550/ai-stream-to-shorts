import json
import ollama


MODEL_NAME = "llama3.2:3b"
BATCH_SIZE = 2


def analyze_batch(moments):
    """Analyze a small batch of moments using local Llama."""

    prompt_data = [
        {
            "index": index,
            "duration": moment["duration"],
            "text": moment["text"]
        }
        for index, moment in enumerate(moments)
    ]

    prompt = f"""
You are an expert YouTube Shorts editor.

Analyze each video moment independently.

Give each moment a score from 0 to 100.

Consider:
- Excitement and emotion
- Humor and reactions
- Surprising moments
- Interesting conversation
- Potential viewer engagement

Important:
- Analyze every moment.
- Do not invent events.
- If the transcript is unclear, do not assume what happened.
- Return valid JSON only.

Required format:
{{
  "ranked_moments": [
    {{
      "index": 0,
      "score": 75,
      "reasons": ["Interesting conversation"]
    }}
  ]
}}

Moments:
{json.dumps(prompt_data, ensure_ascii=False)}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
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
    """Rank moments in small batches with individual retries."""

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

        results = analyze_batch(batch)

        for index, moment in enumerate(batch):
            if index not in results:
                print(
                    f"Retrying moment {batch_start + index + 1} individually..."
                )

                retry_results = analyze_batch([moment])

                if 0 not in retry_results:
                    raise ValueError(
                        f"AI could not rank moment {batch_start + index + 1}."
                    )

                result = retry_results[0]
            else:
                result = results[index]

            ranked.append({
                **moment,
                "score": result["score"],
                "reasons": result["reasons"]
            })

    return sorted(
        ranked,
        key=lambda item: item["score"],
        reverse=True
    )
