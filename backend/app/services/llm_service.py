"""
LLM Service for generating dynamic musical interpretations.
Uses Groq API (via httpx) to analyze the mapped musical data and generate text.
"""

import json
from app.config import settings

class LLMService:
    def __init__(self):
        pass

    async def generate_interpretations(
        self, 
        metadata_list: list[dict], 
        mapping_result
    ) -> dict:
        """
        Generate dynamic musical interpretations for each event and a global summary.
        Uses a single batch prompt to avoid multiple API calls.
        """
        if settings.USE_MOCK_EMBEDDINGS or not settings.GROQ_API_KEY:
            return self._generate_mock_interpretations(metadata_list, mapping_result)

        events_for_prompt = []
        for meta, note in zip(metadata_list, mapping_result.notes):
            events_for_prompt.append({
                "id": meta["id"],
                "title": meta["title"],
                "category": meta["category"],
                "sentiment": meta["sentiment"],
                "pitch": note.pitch,
                "velocity": note.velocity,
                "duration": note.duration,
                "chords": note.chord
            })

        prompt = f"""
You are an expert musicologist and a poet. 
We have mapped historical events to musical parameters via Data Sonification.

Overall composition mood: {mapping_result.mood}
Tempo: {mapping_result.tempo} BPM
Scale: {mapping_result.scale.get('name', 'Pentatonic')}

The data list below contains each event's musical parameters (pitch, velocity, duration, chords).
PLEASE WRITE ALL RESPONSES IN ENGLISH WITH A HIGHLY POETIC TONE.

Task 1: For each event, write a 1-2 sentence POETIC musical interpretation explaining HOW the event's emotion relates to its assigned musical parameters. (e.g., "The harshness of the G4 note echoes the desperation of a gunpowder-scented morning, blending into sorrow with the Am7 chord...")
Task 2: In 'global_interpretation', write a 2-3 sentence POETIC paragraph summarizing the emotional sonic journey of these events.

Data:
{json.dumps(events_for_prompt, indent=2)}

Return ONLY a valid JSON object in the following format (No Markdown, just raw JSON):
{{
  "global_interpretation": "...",
  "events": {{
    "e1": "...",
    "e2": "..."
  }}
}}
"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Extract JSON if Llama-3 adds markdown block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            result_json = json.loads(content)
            return result_json

        except Exception as e:
            import traceback
            error_msg = f"[WARN] LLM interpretation failed: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return self._generate_mock_interpretations(metadata_list, mapping_result)

    def _generate_mock_interpretations(self, metadata_list, mapping_result):
        """Fallback if API fails or mock mode is enabled."""
        result = {
            "global_interpretation": (
                f"This composition is generated from {len(metadata_list)} clustered Vietnam War records. "
                f"The overall mood is {mapping_result.mood}. "
                f"Conflict-heavy clusters produce darker tones and heavier durations, "
                f"while peace-related clusters move toward softer, more stable harmonic structures."
            ),
            "events": mapping_result.interpretations
        }
        return result
