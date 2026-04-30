"""
Pydantic schemas for API request/response validation.
These models ensure frontend-backend data format compatibility.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PipelineStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EventCategory(str, Enum):
    CONFLICT = "conflict"
    PEACE_TALKS = "peace_talks"
    CIVILIAN_IMPACT = "civilian_impact"
    POLITICAL_TRANSITION = "political_transition"
    UNCERTAINTY = "uncertainty"


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    """Response after uploading a dataset."""
    task_id: str
    status: str = "processing"
    message: str = "Pipeline started successfully"


class PipelineStep(BaseModel):
    """Individual pipeline step status."""
    name: str
    status: str  # pending | active | completed
    description: str


class PipelineStatusResponse(BaseModel):
    """Response for pipeline status polling."""
    task_id: str
    status: PipelineStatusEnum
    progress_pct: int = Field(ge=0, le=100)
    current_step: int
    total_steps: int = 5
    steps: list[PipelineStep]
    error: Optional[str] = None


class EventResult(BaseModel):
    """
    Single historical event with embedding coordinates and musical interpretation.
    Matches the frontend mockEvents format exactly.
    """
    id: str
    date: str
    title: str
    category: str
    sentiment: float = Field(ge=-1.0, le=1.0)
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    musicalInterpretation: str


class MusicMetadata(BaseModel):
    """Musical analysis metadata for the generated soundscape."""
    tempo_bpm: int
    scale: str
    scale_name: str
    chord_progression: str
    progression_name: str
    mood: str
    total_notes: int
    duration_seconds: float


class PlaybackNote(BaseModel):
    """Compact note data used by the frontend Web Audio player."""
    pitch: int
    velocity: int
    start_time: float
    duration: float


class LyricLine(BaseModel):
    """Single synchronized lyric line for the generated MIDI composition."""
    start_beat: float
    text: str


class PipelineResultResponse(BaseModel):
    """Complete pipeline result — events + music metadata + download links."""
    task_id: str
    events: list[EventResult]
    music_metadata: MusicMetadata
    midi_url: str
    playback_notes: list[PlaybackNote] = Field(default_factory=list)
    interpretation_text: str
    lyrics: Optional[list[LyricLine]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    services: dict
