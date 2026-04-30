"""AI-ready historical emotion and theme analysis."""

import json
from typing import Any

from app.config import settings


CORE_THEMES = ["farewell", "mortality", "war", "hope", "guilt", "transition", "legacy"]


KEYWORDS = {
    "farewell": ["farewell", "departure", "evacuation", "closure", "ending", "leave"],
    "mortality": ["killed", "death", "mortality", "loss", "grief", "violence"],
    "war": ["war", "troops", "offensive", "combat", "military", "vietnam"],
    "hope": ["peace", "hope", "festival", "communal", "accord", "negotiation"],
    "guilt": ["state violence", "public grief", "unease", "shock"],
    "transition": ["transition", "expanded", "end", "closure", "changed"],
    "legacy": ["legacy", "memory", "symbol", "cultural", "images"],
}


def calculateThemeSimilarity(event_analysis: dict[str, Any]) -> dict[str, float]:
    """Score an analysis against the archive's core themes."""
    text = " ".join([
        event_analysis.get("dominant_emotion", ""),
        " ".join(event_analysis.get("themes", [])),
        event_analysis.get("summary", ""),
    ]).lower()
    scores = {}
    for theme in CORE_THEMES:
        hits = sum(1 for keyword in KEYWORDS[theme] if keyword in text)
        direct = 1.0 if theme in event_analysis.get("themes", []) else 0.0
        scores[theme] = round(min(1.0, direct + hits * 0.22), 2)
    return scores


def mapEventToCoreThemes(event_analysis: dict[str, Any]) -> list[str]:
    scores = calculateThemeSimilarity(event_analysis)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [theme for theme, score in ranked[:3] if score > 0]


def fallbackAnalyzeEvents(events: list[dict], threshold: str = "farewell") -> list[dict]:
    """Deterministic local analysis so the demo works without network access."""
    analyzed = []
    threshold = (threshold or "farewell").lower()

    for index, event in enumerate(events):
        text = " ".join([
            event.get("title", ""),
            event.get("description", ""),
            event.get("historical_context", ""),
            threshold,
        ]).lower()

        raw_scores = {
            theme: sum(1 for keyword in keywords if keyword in text)
            for theme, keywords in KEYWORDS.items()
        }
        if threshold in raw_scores:
            raw_scores[threshold] += 2

        ranked_themes = [
            theme for theme, score in sorted(raw_scores.items(), key=lambda item: item[1], reverse=True)
            if score > 0
        ][:3] or [threshold, "transition"]

        if "peace" in text or "accord" in text:
            emotion = "fragile peace"
        elif "woodstock" in text or "counterculture" in text:
            emotion = "resistance mixed with hope"
        elif "kent state" in text or "killed" in text:
            emotion = "grief and moral shock"
        elif "saigon" in text or "evacuation" in text:
            emotion = "farewell and unresolved loss"
        elif "offensive" in text or "combat" in text:
            emotion = "fear and war shock"
        else:
            emotion = "weary transition"

        intensity = min(1.0, 0.45 + raw_scores.get("war", 0) * 0.14 + raw_scores.get("mortality", 0) * 0.16 + index * 0.03)
        historical_weight = min(1.0, 0.58 + raw_scores.get("legacy", 0) * 0.12 + raw_scores.get("transition", 0) * 0.1 + raw_scores.get("war", 0) * 0.08)
        summary = (
            f"{event['title']} becomes a {emotion} fragment, carrying "
            f"{', '.join(ranked_themes)} into the threshold."
        )

        analysis = {
            "id": f"e{index + 1}",
            "dominant_emotion": emotion,
            "themes": ranked_themes,
            "intensity": round(intensity, 2),
            "historical_weight": round(historical_weight, 2),
            "summary": summary,
        }
        analysis["theme_similarity"] = calculateThemeSimilarity(analysis)
        analysis["core_themes"] = mapEventToCoreThemes(analysis)
        analyzed.append({**event, "analysis": analysis})

    return analyzed


async def analyzeEventsWithAI(events: list[dict], threshold: str = "farewell") -> tuple[list[dict], str]:
    """Use Groq when available; otherwise return deterministic local analysis."""
    fallback = fallbackAnalyzeEvents(events, threshold)
    if not settings.GROQ_API_KEY:
        return fallback, "fallback_rule_based_analysis"

    try:
        import httpx

        prompt = (
            "Return ONLY valid JSON. Analyze these historical events for an AI memory-to-melody artwork. "
            "Do not use user-provided emotions; infer them from historical context. "
            "Format: {\"events\":[{\"id\":\"e1\",\"dominant_emotion\":\"...\","
            "\"themes\":[\"farewell\"],\"intensity\":0.0,\"historical_weight\":0.0,"
            "\"summary\":\"...\"}]}. "
            f"Core themes: {CORE_THEMES}. Threshold: {threshold}. "
            f"Events: {json.dumps(events, ensure_ascii=False)}"
        )
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.35,
                },
            )
        response.raise_for_status()
        parsed = json.loads(response.json()["choices"][0]["message"]["content"])
        by_id = {item.get("id"): item for item in parsed.get("events", [])}

        enriched = []
        for fallback_event in fallback:
            analysis = {**fallback_event["analysis"], **by_id.get(fallback_event["analysis"]["id"], {})}
            analysis["theme_similarity"] = calculateThemeSimilarity(analysis)
            analysis["core_themes"] = mapEventToCoreThemes(analysis)
            enriched.append({**fallback_event, "analysis": analysis})
        return enriched, "groq_llama_3_3_70b_analysis"
    except Exception as exc:
        print(f"[AI] Historical analysis unavailable, using deterministic fallback: {exc}")
        return fallback, "fallback_rule_based_analysis"
