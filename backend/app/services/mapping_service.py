"""
Musical Mapping Service — CORE ORIGINAL LOGIC.
Transforms 2D embedding coordinates + metadata into musical parameters.
This is the heart of the data sonification pipeline.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional

from app.core.music_theory import (
    PENTATONIC_SCALES,
    DYLAN_PROGRESSIONS,
    VELOCITY_MIN,
    VELOCITY_MAX,
    DURATION_MIN,
    DURATION_MAX,
    TEMPO_MIN,
    TEMPO_MAX,
    select_scale_by_sentiment,
    select_progression_by_sentiment,
    midi_note_to_name,
)
from app.core.data_transforms import linear_map


class NoteEvent:
    """Represents a single musical note generated from data."""

    def __init__(
        self,
        pitch: int,
        velocity: int,
        duration: float,
        start_time: float,
        chord: Optional[list[str]] = None,
        source_event_id: str = "",
    ):
        self.pitch = pitch
        self.velocity = velocity
        self.duration = duration
        self.start_time = start_time
        self.chord = chord or []
        self.source_event_id = source_event_id

    def __repr__(self):
        return (
            f"NoteEvent(pitch={midi_note_to_name(self.pitch)}, "
            f"vel={self.velocity}, dur={self.duration:.2f}, t={self.start_time:.2f})"
        )


class MappingResult:
    """Result of the musical mapping for the entire dataset."""

    def __init__(self):
        self.notes: list[NoteEvent] = []
        self.tempo: int = 72
        self.scale: dict = {}
        self.progression: dict = {}
        self.mood: str = ""
        self.interpretations: dict[str, str] = {}


class MappingService:
    """
    Maps 2D embedding coordinates + event metadata to musical parameters.

    Mapping Rules:
    - x coordinate → Pitch (pentatonic scale note selection)
    - y coordinate → Velocity (loudness: 40-120 MIDI)
    - cluster_id   → Chord progression (Dylan sequences)
    - date         → Temporal position in composition
    - casualties   → Note duration (more casualties → longer, heavier notes)
    - sentiment    → Tonality (negative → minor, positive → major)
    """

    def __init__(self):
        self._interpretation_templates = self._load_interpretation_templates()

    def _load_interpretation_templates(self) -> dict:
        """Load musical interpretation templates from dylan_chords.json."""
        try:
            chords_path = Path("data/dylan_chords.json")
            if chords_path.exists():
                with open(chords_path, "r") as f:
                    data = json.load(f)
                return data.get("interpretation_templates", {})
        except Exception:
            pass

        # Fallback templates
        return {
            "conflict": "Heavy, distorted tones conveying the weight of armed confrontation.",
            "peace_talks": "A gentle, resolving harmonic movement suggesting cautious optimism.",
            "civilian_impact": "A mournful, sustained melody reflecting the human cost of conflict.",
            "political_transition": "A measured, rhythmic pattern echoing political change.",
            "uncertainty": "Syncopated, restless textures mirroring unresolved tensions.",
        }

    def map_data_to_music(
        self,
        coords_2d: np.ndarray,
        clusters: list[int],
        metadata_list: list[dict],
    ) -> MappingResult:
        """
        Main mapping function — converts data coordinates to musical parameters.

        Args:
            coords_2d: (N, 2) array of 2D embedding coordinates (0-100 range)
            clusters: List of cluster labels
            metadata_list: List of event metadata dicts with keys:
                           date, title, category, sentiment, casualties

        Returns:
            MappingResult with notes, tempo, scale, progression, mood, and interpretations
        """
        result = MappingResult()

        # --- 1. Determine global parameters from data statistics ---
        sentiments = [m.get("sentiment", 0.0) for m in metadata_list]
        avg_sentiment = np.mean(sentiments)

        # Select scale based on overall sentiment
        result.scale = select_scale_by_sentiment(avg_sentiment)

        # Select progression based on dominant cluster sentiment
        result.progression = select_progression_by_sentiment(avg_sentiment)

        # Calculate tempo from data intensity
        all_casualties = [m.get("casualties", 0) for m in metadata_list]
        max_casualties = max(all_casualties) if all_casualties else 0
        avg_casualties = np.mean(all_casualties) if all_casualties else 0

        # More casualties → faster (more intense) tempo
        result.tempo = int(linear_map(avg_casualties, 0, 1000, TEMPO_MIN, TEMPO_MAX))
        result.tempo = max(TEMPO_MIN, min(TEMPO_MAX, result.tempo))

        # Determine overall mood
        result.mood = self._determine_mood(avg_sentiment, avg_casualties)

        # --- 2. Map each data point to a note ---
        scale_notes = result.scale["notes"]
        n_scale_notes = len(scale_notes)

        current_time = 0.0

        for i, (coord, cluster, meta) in enumerate(zip(coords_2d, clusters, metadata_list)):
            x, y = coord[0], coord[1]
            sentiment = meta.get("sentiment", 0.0)
            casualties = meta.get("casualties", 0)
            category = meta.get("category", "uncertainty")
            event_id = meta.get("id", f"e{i+1}")

            # --- Pitch Mapping ---
            # To make the music more meaningful and melodic, we map sentiment to the octave (register)
            # and the x-coordinate to the specific note in the scale.
            
            # 1. Determine Octave based on Sentiment
            if sentiment > 0.4:
                base_octave = 5  # Higher, brighter register for positive events
            elif sentiment > -0.4:
                base_octave = 4  # Mid register for neutral/mixed events
            else:
                base_octave = 3  # Lower, darker register for negative/conflict events
                
            # 2. Determine Note within scale based on X coordinate
            note_in_scale = int(linear_map(x, 0, 100, 0, n_scale_notes - 1))
            note_in_scale = max(0, min(n_scale_notes - 1, note_in_scale))
            
            # Calculate final MIDI pitch
            pitch = scale_notes[note_in_scale] + (base_octave * 12)
            pitch = max(36, min(96, pitch))  # Clamp to reasonable MIDI range

            # --- y → Velocity ---
            velocity = int(linear_map(y, 0, 100, VELOCITY_MIN, VELOCITY_MAX))

            # Sentiment modifier: negative sentiment → softer attack
            if sentiment < -0.5:
                velocity = max(VELOCITY_MIN, velocity - 15)

            # --- casualties → Duration ---
            if max_casualties > 0:
                duration = linear_map(casualties, 0, max_casualties, DURATION_MIN, DURATION_MAX)
            else:
                duration = 1.0  # Default quarter note

            # Sentiment also affects duration: very negative → longer, heavier
            if sentiment < -0.7:
                duration *= 1.5

            duration = max(DURATION_MIN, min(DURATION_MAX, duration))

            # --- cluster → Chord progression assignment ---
            cluster_progression = self._get_cluster_progression(cluster, sentiment)
            chord_names = cluster_progression["chords"]

            # --- Create note event ---
            note = NoteEvent(
                pitch=pitch,
                velocity=velocity,
                duration=duration,
                start_time=current_time,
                chord=chord_names,
                source_event_id=event_id,
            )
            result.notes.append(note)

            # Advance time based on duration
            current_time += duration + 0.25  # Small gap between notes

            # --- Generate musical interpretation for this event ---
            result.interpretations[event_id] = self._generate_interpretation(
                category, sentiment, pitch, velocity, duration, chord_names
            )

        return result

    def _determine_mood(self, avg_sentiment: float, avg_casualties: float) -> str:
        """Determine the overall mood of the composition."""
        if avg_sentiment < -0.5:
            if avg_casualties > 500:
                return "devastated / anguished"
            return "somber / heavy"
        elif avg_sentiment < -0.2:
            return "tired / accepting"
        elif avg_sentiment < 0.2:
            return "uncertain / shifting"
        elif avg_sentiment < 0.5:
            return "cautiously hopeful"
        else:
            return "resolving / peaceful"

    def _get_cluster_progression(self, cluster_id: int, sentiment: float) -> dict:
        """Select a chord progression for a cluster based on sentiment."""
        # Use sentiment to override cluster-based selection
        return select_progression_by_sentiment(sentiment)

    def _generate_interpretation(
        self,
        category: str,
        sentiment: float,
        pitch: int,
        velocity: int,
        duration: float,
        chords: list[str],
    ) -> str:
        """
        Generate a highly dynamic, natural-language musical interpretation for an event.
        Used as a rich fallback if the LLM API is unavailable.
        """
        note_name = midi_note_to_name(pitch)
        chord_str = " - ".join(chords)

        # Dynamic descriptors based on parameters
        if velocity > 90:
            intensity = "thunderous, commanding"
            verb = "strikes with undeniable force"
        elif velocity > 60:
            intensity = "measured, resonant"
            verb = "echoes steadily"
        else:
            intensity = "fragile, whispering"
            verb = "lingers in the air"

        if duration > 2.0:
            length_desc = "endlessly suspended"
        elif duration > 1.0:
            length_desc = "deliberately paced"
        else:
            length_desc = "fleeting, rapid"

        if sentiment > 0.5:
            emotion = "a bright surge of triumph and hope"
        elif sentiment > 0:
            emotion = "a cautious step toward progress"
        elif sentiment > -0.5:
            emotion = "a heavy shadow of uncertainty"
        else:
            emotion = "a dark resonance of profound struggle"

        # Unique category-based poetic starts
        category_poetics = {
            "launch": "Ignition of human ambition:",
            "orbit": "Suspended in the vast silence:",
            "landing": "Contact with the unknown:",
            "crisis": "A sudden rupture in the journey:",
            "triumph": "A monumental leap achieved:",
            "tragedy": "A moment of devastating loss:",
            "conflict": "The violent clash of forces:",
            "peace_talks": "Whispers of reconciliation:",
            "civilian_impact": "The silent toll of history:",
            "political_transition": "The shifting tides of power:"
        }
        
        prefix = category_poetics.get(category.lower(), "A defining moment translated into sound:")

        interpretation = (
            f"{prefix} A {intensity} {note_name} tone {verb}, "
            f"its {length_desc} rhythm reflecting {emotion}. "
            f"The underlying {chord_str} progression grounds the melody in historical weight."
        )

        return interpretation
