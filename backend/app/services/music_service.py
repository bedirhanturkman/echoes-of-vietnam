"""
Music Generation Service.
Creates MIDI files from mapped musical data using MIDIUtil.
"""

import os
from pathlib import Path
from midiutil import MIDIFile

from app.services.mapping_service import MappingResult, NoteEvent
from app.core.music_theory import CHORD_MIDI
from app.config import settings


class MusicService:
    """
    Generate MIDI files from MappingResult data.
    Uses MIDIUtil for pure-Python MIDI creation.
    """

    def generate_midi(self, mapping_result: MappingResult, task_id: str) -> str:
        """
        Generate a MIDI file from the mapping result.

        Args:
            mapping_result: Result from MappingService containing notes, tempo, etc.
            task_id: Task identifier for filename

        Returns:
            Relative URL path to the generated MIDI file
        """
        # Create MIDI file with 2 tracks: melody + chords
        midi = MIDIFile(
            numTracks=2,
            removeDuplicates=True,
            deinterleave=True,
        )

        tempo = mapping_result.tempo
        melody_track = 0
        chord_track = 1
        melody_channel = 0
        chord_channel = 1
        time = 0  # Start at the beginning

        # Track names
        midi.addTrackName(melody_track, time, "Vietnam Echoes - Melody")
        midi.addTrackName(chord_track, time, "Vietnam Echoes - Chords")

        # Set tempo
        midi.addTempo(melody_track, time, tempo)
        midi.addTempo(chord_track, time, tempo)

        # Set instruments
        midi.addProgramChange(melody_track, melody_channel, 0, 0)   # Acoustic Grand Piano
        midi.addProgramChange(chord_track, chord_channel, 0, 24)    # Nylon Guitar (Dylan-esque)

        # --- Add melody notes ---
        for note in mapping_result.notes:
            midi.addNote(
                track=melody_track,
                channel=melody_channel,
                pitch=note.pitch,
                time=note.start_time,
                duration=note.duration,
                volume=note.velocity,
            )

        # --- Add chord accompaniment ---
        self._add_chord_track(midi, chord_track, chord_channel, mapping_result)

        # --- Write to file ---
        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"echoes_{task_id[:8]}.mid"
        filepath = output_dir / filename

        with open(filepath, "wb") as f:
            midi.writeFile(f)

        print(f"[MIDI] MIDI file generated: {filepath}")

        # Return URL path for frontend download
        return f"/output/{filename}"

    def _add_chord_track(
        self,
        midi: MIDIFile,
        track: int,
        channel: int,
        mapping_result: MappingResult,
    ):
        """
        Add chord accompaniment based on the events' chord progressions.
        Chords change based on the data-driven progression assignments.
        """
        if not mapping_result.notes:
            return

        # Group notes by their chord progression
        current_chord_names = None
        chord_start = 0.0
        chord_volume = 60  # Softer than melody

        for note in mapping_result.notes:
            chord_names = note.chord

            if chord_names != current_chord_names:
                # Write previous chord if it existed
                if current_chord_names is not None:
                    chord_duration = note.start_time - chord_start
                    if chord_duration > 0:
                        self._write_chord(
                            midi, track, channel,
                            current_chord_names, chord_start,
                            chord_duration, chord_volume,
                        )

                current_chord_names = chord_names
                chord_start = note.start_time

        # Write the last chord
        if current_chord_names and mapping_result.notes:
            last_note = mapping_result.notes[-1]
            chord_duration = last_note.start_time + last_note.duration - chord_start
            if chord_duration > 0:
                self._write_chord(
                    midi, track, channel,
                    current_chord_names, chord_start,
                    chord_duration, chord_volume,
                )

    def _write_chord(
        self,
        midi: MIDIFile,
        track: int,
        channel: int,
        chord_names: list[str],
        start_time: float,
        duration: float,
        volume: int,
    ):
        """Write a chord (multiple simultaneous notes) to the MIDI file."""
        for chord_name in chord_names:
            midi_notes = CHORD_MIDI.get(chord_name)
            if midi_notes:
                for pitch in midi_notes:
                    midi.addNote(
                        track=track,
                        channel=channel,
                        pitch=pitch,
                        time=start_time,
                        duration=min(duration, 4.0),  # Max 4 beats per chord
                        volume=volume,
                    )

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
