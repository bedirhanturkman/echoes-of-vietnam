"""
AI Composer Service — Gemini-powered music composition.
Sends event data to Gemini and receives a structured multi-track
composition as JSON, which is then converted to MIDI.
"""

import json
import traceback
import random

from app.config import settings
from app.core.music_theory import (
    GM_INSTRUMENTS,
    CATEGORY_INSTRUMENTS,
    CHORD_MIDI,
    CHORD_ROOTS,
    PENTATONIC_SCALES,
    DYLAN_PROGRESSIONS,
)


class AIComposerService:
    """
    Uses Gemini API to compose a multi-instrument musical piece
    based on historical Vietnam War event data.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        from google import genai

        if self._client is None:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    async def compose(
        self,
        metadata_list: list[dict],
        mapping_result,
    ) -> dict:
        """
        Ask Gemini to compose a multi-track musical piece.

        Args:
            metadata_list: List of event metadata dicts
            mapping_result: MappingResult with notes, scale, mood, tempo info

        Returns:
            dict with keys: tempo, time_signature, tracks[]
            Each track has: name, instrument (GM program), channel, notes[]
            Each note has: pitch, start_time, duration, velocity
        """
        try:
            composition = await self._compose_with_gemini(metadata_list, mapping_result)
            if composition and self._validate_composition(composition):
                print(f"[AI] Gemini composed {len(composition.get('tracks', []))} tracks successfully")
                return composition
            else:
                print("[AI] Gemini output invalid, falling back to simple composition")
                return self._fallback_composition(metadata_list, mapping_result)
        except Exception as e:
            print(f"[AI] Gemini composition failed: {e}")
            traceback.print_exc()
            return self._fallback_composition(metadata_list, mapping_result)

    async def _compose_with_gemini(self, metadata_list: list[dict], mapping_result) -> dict:
        """Call Gemini API with structured output to compose music."""
        from google.genai import types

        client = self._get_client()

        # Build the event summary for the prompt
        events_summary = []
        for i, meta in enumerate(metadata_list):
            events_summary.append({
                "order": i + 1,
                "title": meta.get("title", "Unknown event"),
                "date": meta.get("date", ""),
                "category": meta.get("category", "uncertainty"),
                "sentiment": meta.get("sentiment", 0.0),
                "casualties": meta.get("casualties", 0),
            })

        # Build the composition prompt
        prompt = self._build_prompt(events_summary, mapping_result)

        # Call Gemini with structured output
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        # Parse the response
        content = response.text
        if not content:
            raise ValueError("Empty response from Gemini")

        # Clean markdown if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        composition = json.loads(content)
        return composition

    def _build_prompt(self, events_summary: list[dict], mapping_result) -> str:
        """Build a detailed prompt for Gemini to compose music."""

        # Calculate total composition length in beats based on event count
        num_events = len(events_summary)
        total_beats = max(32, num_events * 4)  # At least 32 beats, ~4 beats per event

        prompt = f"""You are a world-class film composer creating a cinematic musical piece for a documentary about the Vietnam War. 

## TASK
Compose a COMPLETE multi-instrument musical piece as structured JSON. The piece must be **harmonious, emotionally powerful, and musically coherent** — like a real film score.

## HISTORICAL CONTEXT
The following {num_events} events from the Vietnam War drive the emotional arc of the piece:

{json.dumps(events_summary, indent=2)}

## MUSICAL DIRECTION
- Overall mood: {mapping_result.mood}
- Suggested tempo: {mapping_result.tempo} BPM
- Scale: {mapping_result.scale.get('name', 'Pentatonic')}
- The piece should tell a story: begin softly, build tension with conflict events, peak at the most devastating moments, and resolve toward the end.

## INSTRUMENTS TO USE (General MIDI program numbers)
You MUST use these exact instrument program numbers:
- Strings Ensemble (program 49, channel 0) — Sustained pads, harmonic foundation
- Cello (program 43, channel 1) — Main melody for conflict/dark moments
- Acoustic Guitar (program 25, channel 2) — Melody for peaceful/folk moments 
- Acoustic Bass (program 33, channel 3) — Bass line, root notes
- Flute (program 74, channel 4) — Counter-melody, ornamental phrases
- Piano (program 0, channel 5) — Chordal accompaniment, transitions

## LYRICS INSTRUCTION
Write poetic, Bob Dylan-esque folk lyrics that tell the story of these events.
- They should reflect the sorrow, uncertainty, and longing for peace during the Vietnam War.
- Structure them with [Verse], [Chorus], and [Bridge].
- Each line of lyrics must be synchronized with a `start_beat` (when the line should appear on screen).
- Make sure the lyrics span the entire {total_beats} beats.

## COMPOSITION RULES
1. **Total length**: approximately {total_beats} beats (in 4/4 time)
2. **Harmony**: All tracks must be in the SAME key. Use chord tones. Avoid dissonance.
3. **Structure**: Create an intro (soft strings), body (melody + accompaniment), climax (full ensemble), outro (strings fade)
4. **Melody**: Write singable, memorable melodic phrases (not random notes). Use stepwise motion and small intervals.
5. **Bass**: Play chord roots on beats 1 and 3. Simple, steady rhythm.
6. **Strings**: Long sustained chords (4-8 beats each). Volume should swell during intense events.
7. **Flute**: Sparse, ornamental — only play in body/climax sections, not every beat.
8. **Piano**: Gentle arpeggiated chords or block chords. Support the melody.
9. **Dynamics**: conflict/civilian_impact events = louder (velocity 80-110), peace_talks = softer (velocity 40-70)
10. **MIDI pitch range**: Keep all notes between 36 and 96.
11. **Velocity range**: Keep all velocities between 30 and 120.

## OUTPUT FORMAT
Return ONLY a valid JSON object with this exact structure:
{{
  "tempo": {mapping_result.tempo},
  "time_signature": "4/4",
  "lyrics": [
    {{"start_beat": 0.0, "text": "[Intro] (Instrumental)"}},
    {{"start_beat": 16.0, "text": "The rivers run with memories untold,"}},
    {{"start_beat": 20.0, "text": "Of soldiers young who never grew old."}}
  ],
  "tracks": [
    {{
      "name": "Strings Ensemble",
      "instrument": 49,
      "channel": 0,
      "notes": [
        {{"pitch": 60, "start_time": 0.0, "duration": 8.0, "velocity": 50}},
        ...more notes
      ]
    }},
    {{
      "name": "Cello Melody",
      "instrument": 43,
      "channel": 1,
      "notes": [...]
    }},
    {{
      "name": "Acoustic Guitar",
      "instrument": 25,
      "channel": 2,
      "notes": [...]
    }},
    {{
      "name": "Bass",
      "instrument": 33,
      "channel": 3,
      "notes": [...]
    }},
    {{
      "name": "Flute",
      "instrument": 74,
      "channel": 4,
      "notes": [...]
    }},
    {{
      "name": "Piano",
      "instrument": 0,
      "channel": 5,
      "notes": [...]
    }}
  ]
}}

IMPORTANT: 
- Each track must have at least 10 notes
- All notes must have valid pitch (36-96), velocity (30-120), positive duration, and non-negative start_time
- Make the music BEAUTIFUL and HARMONIOUS, highly professional cinematic quality
- Provide at least 8 lines of lyrics spanning the song duration"""

        return prompt

    def _validate_composition(self, composition: dict) -> bool:
        """Validate the AI-generated composition has required structure."""
        if not isinstance(composition, dict):
            return False
        if "tracks" not in composition:
            return False
        tracks = composition["tracks"]
        if not isinstance(tracks, list) or len(tracks) == 0:
            return False

        total_notes = 0
        for track in tracks:
            if not isinstance(track, dict):
                return False
            if "notes" not in track or "instrument" not in track:
                return False
            notes = track["notes"]
            if not isinstance(notes, list):
                return False
            for note in notes:
                if not isinstance(note, dict):
                    return False
                required_keys = ["pitch", "start_time", "duration", "velocity"]
                if not all(k in note for k in required_keys):
                    return False
                # Clamp values to valid ranges
                note["pitch"] = max(36, min(96, int(note["pitch"])))
                note["velocity"] = max(30, min(120, int(note["velocity"])))
                note["duration"] = max(0.1, float(note["duration"]))
                note["start_time"] = max(0.0, float(note["start_time"]))
            total_notes += len(notes)

        # Must have at least some notes
        if total_notes < 10:
            print(f"[AI] Composition too sparse: only {total_notes} total notes")
            return False

        if "lyrics" not in composition or not isinstance(composition["lyrics"], list):
            # Not a fatal error, but log it
            print("[AI] Warning: No lyrics array found in composition")
            composition["lyrics"] = []

        return True

    def _fallback_composition(self, metadata_list: list[dict], mapping_result) -> dict:
        """
        Generate a simple but harmonious fallback composition
        if the AI call fails. This is much simpler than the previous
        algorithmic approach — just basic chords + melody.
        """
        tempo = mapping_result.tempo
        scale_notes = mapping_result.scale.get("notes", [60, 62, 64, 67, 69])
        chord_names = mapping_result.progression.get("chords", ["G", "D", "C"])

        tracks = []
        total_beats = max(32, len(metadata_list) * 4)

        # --- Track 1: Strings pad (sustained chords) ---
        strings_notes = []
        t = 0.0
        chord_idx = 0
        while t < total_beats:
            chord_name = chord_names[chord_idx % len(chord_names)]
            midi_notes = CHORD_MIDI.get(chord_name, [60, 64, 67])
            for pitch in midi_notes:
                p = pitch - 12  # Lower octave
                p = max(36, min(84, p))
                strings_notes.append({
                    "pitch": p,
                    "start_time": t,
                    "duration": 8.0,
                    "velocity": 50,
                })
            t += 8.0
            chord_idx += 1

        tracks.append({
            "name": "Strings Ensemble",
            "instrument": 49,
            "channel": 0,
            "notes": strings_notes,
        })

        # --- Track 2: Simple melody ---
        melody_notes = []
        t = 0.0
        for i, meta in enumerate(metadata_list):
            sentiment = meta.get("sentiment", 0.0)
            # Pick scale note based on index
            note_idx = i % len(scale_notes)
            octave = 5 if sentiment > 0 else 4
            pitch = scale_notes[note_idx] + (octave * 12) - 48
            pitch = max(48, min(84, pitch))

            vel = 70 if sentiment > 0 else 85
            dur = 2.0 if abs(sentiment) > 0.5 else 1.0

            melody_notes.append({
                "pitch": pitch,
                "start_time": t,
                "duration": dur,
                "velocity": vel,
            })
            t += dur + 0.5

        tracks.append({
            "name": "Piano Melody",
            "instrument": 0,
            "channel": 1,
            "notes": melody_notes,
        })

        # --- Track 3: Bass ---
        bass_notes = []
        t = 0.0
        chord_idx = 0
        while t < total_beats:
            chord_name = chord_names[chord_idx % len(chord_names)]
            root = CHORD_ROOTS.get(chord_name, 43)
            bass_notes.append({
                "pitch": root,
                "start_time": t,
                "duration": 3.5,
                "velocity": 60,
            })
            t += 4.0
            chord_idx += 1

        tracks.append({
            "name": "Bass",
            "instrument": 33,
            "channel": 2,
            "notes": bass_notes,
        })

        fallback_lyrics = [
            {"start_beat": 0.0, "text": "[Instrumental Intro]"},
            {"start_beat": 8.0, "text": "Shadows fall across the delta,"},
            {"start_beat": 16.0, "text": "Echoes of a distant war."},
            {"start_beat": 24.0, "text": "Waiting for the morning light,"},
            {"start_beat": 32.0, "text": "Wondering what we're fighting for."}
        ]

        return {
            "tempo": tempo,
            "time_signature": "4/4",
            "lyrics": fallback_lyrics,
            "tracks": tracks,
        }
