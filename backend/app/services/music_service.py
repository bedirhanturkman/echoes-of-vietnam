"""
Music Generation Service — JSON-to-MIDI Converter.
Receives AI-composed music as structured JSON and converts it to a MIDI file.
The actual composition is done by AIComposerService (Gemini).
"""

from pathlib import Path
from midiutil import MIDIFile

from app.services.mapping_service import MappingResult
from app.services.ai_composer_service import AIComposerService
from app.core.music_theory import humanize_timing, humanize_velocity
from app.config import settings


class MusicService:
    """
    Orchestrates AI composition and MIDI file generation.
    1. Calls AIComposerService to get a multi-track composition (JSON)
    2. Converts the JSON to a .mid file using MIDIUtil
    """

    def __init__(self):
        self.composer = AIComposerService()

    async def generate_midi_with_ai(
        self,
        mapping_result: MappingResult,
        metadata_list: list[dict],
        task_id: str,
    ) -> tuple[str, list[dict]]:
        """
        Generate a MIDI file using AI-composed music.

        Args:
            mapping_result: MappingResult with scale, mood, tempo context
            metadata_list: Event metadata for AI prompt context
            task_id: Task identifier for filename

        Returns:
            Tuple of (Relative URL path to MIDI file, lyrics list)
        """
        # Step 1: Get AI composition
        print("[MUSIC] Requesting AI composition from Gemini...")
        composition = await self.composer.compose(metadata_list, mapping_result)

        # Step 2: Convert JSON to MIDI
        midi_url = self._json_to_midi(composition, task_id)
        
        lyrics = composition.get("lyrics", [])

        return midi_url, lyrics

    def _json_to_midi(self, composition: dict, task_id: str) -> str:
        """
        Convert AI-generated composition JSON to a MIDI file.

        Args:
            composition: dict with tempo, tracks[], each track with notes[]
            task_id: Task identifier for filename

        Returns:
            Relative URL path to the generated MIDI file
        """
        tracks = composition.get("tracks", [])
        num_tracks = len(tracks)

        if num_tracks == 0:
            raise ValueError("Composition has no tracks")

        midi = MIDIFile(
            numTracks=num_tracks,
            removeDuplicates=True,
            deinterleave=True,
        )

        tempo = composition.get("tempo", 72)

        # Process each track
        total_notes = 0
        for track_idx, track_data in enumerate(tracks):
            track_name = track_data.get("name", f"Track {track_idx}")
            instrument = int(track_data.get("instrument", 0))
            channel = int(track_data.get("channel", track_idx))
            notes = track_data.get("notes", [])

            # Ensure channel is valid (0-15) and not 9 unless it's drums
            channel = channel % 16

            # Set track metadata
            midi.addTrackName(track_idx, 0, track_name)
            midi.addTempo(track_idx, 0, tempo)

            # Set instrument (program change)
            # Channel 9 is reserved for drums in GM — don't set program change
            if channel != 9:
                midi.addProgramChange(track_idx, channel, 0, instrument)

            # Add notes
            for note_data in notes:
                pitch = max(36, min(96, int(note_data.get("pitch", 60))))
                start_time = max(0.0, float(note_data.get("start_time", 0)))
                duration = max(0.1, float(note_data.get("duration", 1.0)))
                velocity = max(30, min(120, int(note_data.get("velocity", 80))))

                midi.addNote(
                    track=track_idx,
                    channel=channel,
                    pitch=pitch,
                    time=humanize_timing(start_time),
                    duration=duration,
                    volume=humanize_velocity(velocity, 3),
                )
                total_notes += 1

        # Write to file
        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"echoes_{task_id[:8]}.mid"
        filepath = output_dir / filename

        with open(filepath, "wb") as f:
            midi.writeFile(f)

        print(
            f"[MIDI] AI-composed MIDI saved: {filepath} "
            f"({num_tracks} tracks, {total_notes} notes, {tempo} BPM)"
        )

        return f"/output/{filename}"

    def get_duration_seconds(self, mapping_result: MappingResult) -> float:
        """Calculate the total duration of the composition in seconds."""
        if not mapping_result.notes:
            return 0.0

        last_note = mapping_result.notes[-1]
        total_beats = last_note.start_time + last_note.duration
        beats_per_second = mapping_result.tempo / 60.0

        if beats_per_second > 0:
            return total_beats / beats_per_second
        return 0.0
