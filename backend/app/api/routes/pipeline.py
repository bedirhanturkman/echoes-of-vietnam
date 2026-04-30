"""
Pipeline API endpoints.
Handles file upload, pipeline status polling, and result retrieval.
"""

import asyncio
import hashlib
import json
from typing import Optional
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Form, Request
from midiutil import MIDIFile
import pandas as pd

from app.tasks.task_manager import task_manager
from app.core.pipeline_orchestrator import PipelineOrchestrator
from app.config import settings
from app.services.data_ingestion import DataIngestionService
from app.services.embedding_service import EmbeddingService
from app.services.reduction_service import ReductionService
from app.services.historical_archive_service import HistoricalArchiveService
from app.services.historical_analysis_service import analyzeEventsWithAI
from app.models.schemas import (
    UploadResponse,
    PipelineStatusResponse,
    PipelineResultResponse,
    PipelineStatusEnum,
)

router = APIRouter()
orchestrator = PipelineOrchestrator()
ingestion = DataIngestionService()
embedding_service = EmbeddingService()
reduction_service = ReductionService()
archive_service = HistoricalArchiveService()

MOOD_CONFIGS = {
    "tired_accepting": {
        "label": "Tired / Accepting",
        "tempo": 72,
        "scale": "A minor pentatonic",
        "notes": [57, 60, 62, 64, 67],
        "progression": ["G", "D", "Am7"],
        "motif": [0, 1, -1],
        "duration_factor": 1.18,
        "velocity_boost": -4,
    },
    "dark_conflict": {
        "label": "Dark / Conflict",
        "tempo": 96,
        "scale": "E minor pentatonic",
        "notes": [52, 55, 57, 59, 62],
        "progression": ["Em", "C", "G", "D"],
        "motif": [0, -1, 2, -2],
        "duration_factor": 0.82,
        "velocity_boost": 12,
    },
    "hopeful_peace": {
        "label": "Hopeful / Peace",
        "tempo": 84,
        "scale": "G major pentatonic",
        "notes": [55, 57, 59, 62, 64],
        "progression": ["G", "D", "C"],
        "motif": [0, 2, 1],
        "duration_factor": 0.95,
        "velocity_boost": 2,
    },
}

CHORDS = {
    "C": [60, 64, 67],
    "D": [62, 66, 69],
    "Em": [52, 55, 59],
    "G": [55, 59, 62],
    "Am7": [57, 60, 64, 67],
}

VALID_MOODS = set(MOOD_CONFIGS.keys())

CATEGORY_SHIFT = {
    "conflict": -2,
    "civilian_impact": -1,
    "uncertainty": 0,
    "political_transition": 1,
    "peace_talks": 2,
}

CATEGORY_COORDS = {
    "conflict": {"x": 18, "y": 28},
    "peace_talks": {"x": 78, "y": 78},
    "civilian_impact": {"x": 28, "y": 36},
    "political_transition": {"x": 58, "y": 48},
    "uncertainty": {"x": 42, "y": 55},
}

EMOTION_TO_CATEGORY = {
    "grief": "civilian_impact",
    "fear": "conflict",
    "shock": "conflict",
    "resistance": "political_transition",
    "hope": "peace_talks",
    "peace": "peace_talks",
    "farewell": "political_transition",
    "transition": "political_transition",
    "loss": "civilian_impact",
}

EMOTION_SCALE_HINTS = {
    "grief": "minor scale, low octave, descending phrase",
    "fear": "low octave, dissonant neighbor tone",
    "hope": "major interval, warmer rhythm",
    "peace": "slow tempo, consonant chord color",
    "farewell": "descending motif",
    "transition": "suspended or unresolved chord",
    "resistance": "stronger rhythm and accent",
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))


def _seed_float(seed_text: str, index: int) -> float:
    digest = hashlib.sha256(f"{seed_text}:{index}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _scale_pitch(scale: list[int], index: int, octave_shift: int = 0) -> int:
    octave = index // len(scale)
    wrapped = index % len(scale)
    return int(_clamp(scale[wrapped] + octave * 12 + octave_shift, 36, 96))


def _category_from_analysis(analysis: dict) -> str:
    text = " ".join([
        analysis.get("dominant_emotion", ""),
        " ".join(analysis.get("themes", [])),
    ]).lower()
    for keyword, category in EMOTION_TO_CATEGORY.items():
        if keyword in text:
            return category
    return "uncertainty"


def _sentiment_from_analysis(analysis: dict) -> float:
    text = " ".join([
        analysis.get("dominant_emotion", ""),
        " ".join(analysis.get("themes", [])),
    ]).lower()
    value = 0.0
    if any(word in text for word in ["grief", "fear", "shock", "war", "mortality", "loss"]):
        value -= 0.55
    if any(word in text for word in ["hope", "peace", "legacy"]):
        value += 0.45
    if "resistance" in text:
        value += 0.12
    return round(_clamp(value, -1, 1), 2)


def _musical_mapping_for_event(event: dict, chord: str, mood_label: str) -> dict:
    analysis = event.get("analysis", {})
    emotion = analysis.get("dominant_emotion", "weary transition")
    text = " ".join([emotion, " ".join(analysis.get("themes", []))]).lower()
    scale_hint = "pentatonic folk scale"
    for keyword, hint in EMOTION_SCALE_HINTS.items():
        if keyword in text:
            scale_hint = hint
            break
    return {
        "scale": scale_hint,
        "chord": chord,
        "motif": "descending farewell phrase" if "farewell" in text else "event-shaped folk motif",
        "tempoEffect": f"{mood_label} with intensity {analysis.get('intensity', 0.5)}",
        "velocityEffect": f"historical weight {analysis.get('historical_weight', 0.5)} shapes accent strength",
    }


def _archive_events_to_dataframe(analyzed_events: list[dict]) -> pd.DataFrame:
    rows = []
    for event in analyzed_events:
        analysis = event.get("analysis", {})
        intensity = float(analysis.get("intensity", 0.5))
        historical_weight = float(analysis.get("historical_weight", 0.5))
        rows.append({
            "date": event["date"],
            "title": event["title"],
            "location": " / ".join(event.get("region", ["Archive"])),
            "category": _category_from_analysis(analysis),
            "sentiment": _sentiment_from_analysis(analysis),
            "casualties": int(round((intensity * 6500) + (historical_weight * 3500))),
            "description": event.get("description", ""),
            "historical_context": event.get("historical_context", ""),
            "dominant_emotion": analysis.get("dominant_emotion", "weary transition"),
            "themes": ", ".join(analysis.get("themes", [])),
            "analysis_summary": analysis.get("summary", ""),
            "intensity": intensity,
            "historical_weight": historical_weight,
            "theme_similarity": json.dumps(analysis.get("theme_similarity", {})),
            "core_themes": ", ".join(analysis.get("core_themes", [])),
        })

    df = pd.DataFrame(rows)
    return ingestion._clean_and_validate(df)


def _mood_point(point: dict, mood_id: str, category: str, sentiment: float, index: int) -> dict:
    """Project the same semantic point into a mood-specific visual space."""
    x = float(point.get("x", 50))
    y = float(point.get("y", 50))

    if mood_id == "dark_conflict":
        x = 100 - x * 0.82
        y = y * 0.72 + 10
        if category == "conflict":
            x -= 10
            y -= 8
    elif mood_id == "hopeful_peace":
        x = x * 0.78 + 17
        y = 100 - ((100 - y) * 0.7 + 12)
        if category == "peace_talks":
            x += 9
            y += 6
    else:
        x = 50 + (x - 50) * 0.68
        y = 50 + (y - 50) * 0.82

    x += (_seed_float(f"{mood_id}:{category}", index) - 0.5) * 6
    y += sentiment * (8 if mood_id == "hopeful_peace" else -5 if mood_id == "dark_conflict" else 3)

    return {
        **point,
        "x": round(_clamp(x, 5, 95), 1),
        "y": round(_clamp(y, 5, 95), 1),
    }


async def _generate_ai_embedding_points(df, seed_text: str) -> tuple[list[dict], str]:
    fallback_points = []
    for index, row in df.iterrows():
        category = row.get("category", "uncertainty")
        fallback = CATEGORY_COORDS.get(category, CATEGORY_COORDS["uncertainty"])
        sentiment = float(row.get("sentiment", 0.0))
        fallback_points.append({
            "id": f"e{index + 1}",
            "x": round(_clamp(fallback["x"] + (_seed_float(seed_text, index + 200) - 0.5) * 20, 5, 95), 1),
            "y": round(_clamp(fallback["y"] + sentiment * 18 + (_seed_float(seed_text, index + 400) - 0.5) * 16, 5, 95), 1),
            "category": category,
        })

    try:
        titles = df["title"].tolist()
        metadata = df.apply(
            lambda row: {
                "date": row.get("date_str", ""),
                "location": row.get("location", "Unknown"),
                "category": row.get("category", "uncertainty"),
                "sentiment": row.get("sentiment", 0.0),
            },
            axis=1,
        ).tolist()
        embeddings = await embedding_service.generate_embeddings(titles, metadata)
        coords = reduction_service.reduce_to_2d(embeddings)
        points = []
        for index, row in df.iterrows():
            points.append({
                "id": f"e{index + 1}",
                "x": round(float(coords[index][0]), 1),
                "y": round(float(coords[index][1]), 1),
                "category": row.get("category", "uncertainty"),
            })
        return points, "gemini_embeddings"
    except Exception as exc:
        print(f"[AI] Gemini embeddings unavailable, using deterministic fallback: {exc}")
        return fallback_points, "fallback_embeddings"


async def _generate_groq_interpretations(events: list[dict], mood_label: str) -> tuple[str, dict, str]:
    fallback_global = (
        f"This composition uses {mood_label} to translate historical records into melody, "
        "bass, and chord layers. Each event shapes timing, pitch, and intensity."
    )
    fallback_events = {
        event["id"]: f"{event['title']} is translated into a musical gesture shaped by {event['category'].replace('_', ' ')}."
        for event in events
    }

    if not settings.GROQ_API_KEY:
        return fallback_global, fallback_events, "fallback_no_groq_key"

    try:
        import httpx

        prompt_events = [
            {
                "id": event["id"],
                "date": event["date"],
                "title": event["title"],
                "category": event["category"],
                "sentiment": event["sentiment"],
            }
            for event in events[:30]
        ]
        prompt = (
            "Return ONLY valid JSON. Write concise poetic interpretations for a Vietnam War "
            f"data sonification in mood '{mood_label}'. Format: "
            '{"global_interpretation":"...","events":{"e1":"..."}}. '
            f"Events: {json.dumps(prompt_events, ensure_ascii=False)}"
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                    "temperature": 0.7,
                },
            )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return (
            parsed.get("global_interpretation", fallback_global),
            parsed.get("events", fallback_events),
            "groq_llama_3_3_70b",
        )
    except Exception as exc:
        print(f"[AI] Groq interpretation unavailable, using deterministic fallback: {exc}")
        return fallback_global, fallback_events, "fallback_groq_error"


async def _generate_backend_soundscape(
    df,
    mood_id: str,
    request: Request,
    embedding_points: Optional[list[dict]] = None,
    embedding_source: Optional[str] = None,
    analysis_source: Optional[str] = None,
    query_meta: Optional[dict] = None,
) -> dict:
    mood = MOOD_CONFIGS.get(mood_id, MOOD_CONFIGS["tired_accepting"])
    seed_text = df.to_json(orient="records") + mood_id
    max_casualties = max([int(v) for v in df["casualties"].tolist()] or [0])
    beat = 60 / mood["tempo"]
    melody = []
    cursor = 0.0

    events = []
    if embedding_points is None or embedding_source is None:
        embedding_points, embedding_source = await _generate_ai_embedding_points(
            df,
            df.to_json(orient="records"),
        )
    point_by_id = {point["id"]: point for point in embedding_points}

    for index, row in df.iterrows():
        event_id = f"e{index + 1}"
        category = row.get("category", "uncertainty")
        sentiment = float(row.get("sentiment", 0.0))
        casualties = max(0, int(row.get("casualties", 0)))
        casualty_weight = casualties / max_casualties if max_casualties > 0 else 0.35
        intensity = float(row.get("intensity", abs(sentiment)))
        historical_weight = float(row.get("historical_weight", casualty_weight if max_casualties > 0 else 0.5))
        dominant_emotion = row.get("dominant_emotion", "")
        themes = [
            item.strip()
            for item in str(row.get("themes", "")).split(",")
            if item.strip()
        ]
        chord = mood["progression"][index % len(mood["progression"])]
        chord_notes = CHORDS.get(chord, CHORDS["G"])
        category_shift = CATEGORY_SHIFT.get(category, 0)
        seeded_offset = int(_seed_float(seed_text, index) * len(mood["notes"]))
        base_index = index + round((sentiment + 1) * 1.5) + category_shift + seeded_offset
        phrase_beats = _clamp(2.2 + historical_weight * 0.9 + intensity * 0.55, 2.2, 3.9) * mood["duration_factor"]
        phrase_duration = phrase_beats * beat
        velocity = 58 + abs(sentiment) * 14 + intensity * 18 + historical_weight * 12 + mood["velocity_boost"]

        def add_note(pitch, start, duration, vel, role):
            melody.append({
                "id": f"{event_id}-{role}-{len(melody)}",
                "pitch": int(round(pitch)),
                "startTime": round(start, 3),
                "duration": round(duration, 3),
                "velocity": int(round(_clamp(vel, 1, 127))),
                "eventId": event_id,
                "category": category,
                "chord": chord,
                "role": role,
            })

        add_note(chord_notes[0] - 12, cursor, phrase_duration, 46 + casualty_weight * 18 + mood["velocity_boost"], "bass")
        for chord_index, pitch in enumerate(chord_notes):
            add_note(pitch, cursor + chord_index * 0.015, phrase_duration * 0.9, 34 + chord_index * 4, "chord")
            arpeggio_start = cursor + (0.5 + chord_index * 0.42) * beat
            if arpeggio_start < cursor + phrase_duration:
                add_note(
                    pitch + (12 if mood_id == "hopeful_peace" else 0),
                    arpeggio_start,
                    0.32 * beat,
                    42 + chord_index * 5 + casualty_weight * 10,
                    "harmony",
                )
        for motif_index, offset in enumerate(mood["motif"]):
            jitter = 0.12 * beat if _seed_float(seed_text, index * 10 + motif_index) > 0.6 else 0
            note_duration = _clamp((0.42 + casualty_weight * 0.28) * beat, 0.18, 0.72)
            octave_shift = -12 if mood_id == "dark_conflict" else (12 if mood_id == "hopeful_peace" and sentiment > -0.3 else 0)
            if "fear" in str(dominant_emotion).lower():
                octave_shift -= 12
            melodic_offset = -motif_index if "farewell" in themes else offset + motif_index
            add_note(
                _scale_pitch(mood["notes"], base_index + melodic_offset, octave_shift),
                cursor + motif_index * (0.52 * beat) + jitter,
                note_duration,
                velocity,
                "melody",
            )

        beat_steps = 4 if mood_id != "dark_conflict" else 6
        for beat_index in range(beat_steps):
            beat_start = cursor + beat_index * (phrase_duration / beat_steps)
            if beat_start >= cursor + phrase_duration:
                continue
            drum_pitch = 36 if beat_index % 2 == 0 else 42
            if beat_index == 2 or (mood_id == "dark_conflict" and beat_index in {1, 4}):
                drum_pitch = 38
            add_note(
                drum_pitch,
                beat_start,
                0.08,
                42 + casualty_weight * 38 + (12 if mood_id == "dark_conflict" else 0),
                "beat",
            )

        point = _mood_point(point_by_id.get(event_id, {"id": event_id, "x": 50, "y": 50, "category": category}), mood_id, category, sentiment, index)
        event = {
            "id": event_id,
            "date": row.get("date_str", ""),
            "title": row.get("title", ""),
            "location": row.get("location", "Unknown"),
            "category": category,
            "sentiment": sentiment,
            "description": row.get("description", ""),
            "historicalContext": row.get("historical_context", ""),
            "dominantEmotion": dominant_emotion,
            "themes": themes,
            "intensity": round(intensity, 2),
            "historicalWeight": round(historical_weight, 2),
            "aiSummary": row.get("analysis_summary", ""),
            "coreThemes": [
                item.strip()
                for item in str(row.get("core_themes", "")).split(",")
                if item.strip()
            ],
            "x": point["x"],
            "y": point["y"],
            "musicalInterpretation": f"{mood['label']} maps this event through {chord}, shaping melody, bass, and harmony from its historical weight.",
            "musicalMapping": _musical_mapping_for_event(
                {"analysis": {
                    "dominant_emotion": dominant_emotion,
                    "themes": themes,
                    "intensity": intensity,
                    "historical_weight": historical_weight,
                }},
                chord,
                mood["label"],
            ),
        }
        events.append(event)
        cursor += phrase_duration + 0.18

    embedding_points = [
        _mood_point(
            point,
            mood_id,
            point.get("category", "uncertainty"),
            float(df.iloc[index].get("sentiment", 0.0)) if index < len(df) else 0.0,
            index,
        )
        for index, point in enumerate(embedding_points)
    ]

    melody = sorted(melody, key=lambda note: (note["startTime"], note["pitch"]))
    interpretation_text, event_interpretations, interpretation_source = await _generate_groq_interpretations(events, mood["label"])
    for event in events:
        event["musicalInterpretation"] = event_interpretations.get(event["id"], event["musicalInterpretation"])

    midi_url = _write_direct_midi(melody, mood["tempo"], mood_id)
    duration = round(max((note["startTime"] + note["duration"] for note in melody), default=0), 1)

    return {
        "events": events,
        "embeddingPoints": embedding_points,
        "melody": melody,
        "metadata": {
            "tempo": mood["tempo"],
            "scale": mood["scale"],
            "progression": " - ".join(mood["progression"]),
            "mood": mood["label"],
            "duration": duration,
            "noteCount": len(melody),
            "ai": {
                "embeddingModel": embedding_source,
                "interpretationModel": interpretation_source,
                "analysisModel": analysis_source or "uploaded_dataset_fields",
            },
            "archiveQuery": query_meta or {},
            "folkInspiration": (
                "Rather than copying Bob Dylan's melodies, the system models broad 1970s folk "
                "harmony principles: simple I-IV-V progressions, acoustic phrasing, descending "
                "farewell motifs, and unresolved transitions."
            ),
        },
        "interpretationText": interpretation_text,
        "midiUrl": str(request.base_url).rstrip("/") + midi_url,
    }


async def _generate_all_backend_soundscapes(
    df,
    request: Request,
    selected_mood: str,
    analysis_source: Optional[str] = None,
    query_meta: Optional[dict] = None,
) -> dict:
    embedding_points, embedding_source = await _generate_ai_embedding_points(
        df,
        df.to_json(orient="records"),
    )
    backend_to_frontend = {
        "tired_accepting": "tired",
        "dark_conflict": "dark",
        "hopeful_peace": "hopeful",
    }
    variants = {}

    results = await asyncio.gather(*[
        _generate_backend_soundscape(
            df,
            mood_id,
            request,
            embedding_points=embedding_points,
            embedding_source=embedding_source,
            analysis_source=analysis_source,
            query_meta=query_meta,
        )
        for mood_id in MOOD_CONFIGS
    ])

    for mood_id, result in zip(MOOD_CONFIGS.keys(), results):
        variants[backend_to_frontend[mood_id]] = result

    selected_frontend_mood = backend_to_frontend.get(selected_mood, "tired")
    selected_result = variants[selected_frontend_mood]

    return {
        **selected_result,
        "selectedMood": selected_frontend_mood,
        "variants": variants,
    }


def _write_direct_midi(melody: list[dict], tempo: int, mood_id: str) -> str:
    role_channel = {"melody": 0, "chord": 1, "bass": 2, "harmony": 3, "beat": 9}
    role_program = {"melody": 0, "chord": 24, "bass": 32, "harmony": 48, "beat": 0}
    role_track = {"melody": 0, "chord": 1, "bass": 2, "harmony": 3, "beat": 4}
    midi = MIDIFile(numTracks=5, removeDuplicates=True, deinterleave=True)
    for role, track in role_track.items():
        channel = role_channel[role]
        midi.addTrackName(track, 0, role.title())
        midi.addTempo(track, 0, tempo)
        if channel != 9:
            midi.addProgramChange(track, channel, 0, role_program[role])

    for note in melody:
        role = note.get("role", "melody")
        track = role_track.get(role, 0)
        channel = role_channel.get(role, 0)
        lower_pitch = 35 if role == "beat" else 36
        upper_pitch = 81 if role == "beat" else 96
        midi.addNote(
            track=track,
            channel=channel,
            pitch=max(lower_pitch, min(upper_pitch, int(note["pitch"]))),
            time=float(note["startTime"]) * tempo / 60,
            duration=max(0.1, float(note["duration"]) * tempo / 60),
            volume=int(note["velocity"]),
        )

    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"echoes_direct_{mood_id}_{uuid4().hex[:8]}.mid"
    filepath = output_dir / filename
    with open(filepath, "wb") as midi_file:
        midi.writeFile(midi_file)
    return f"/output/{filename}"


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_data(
    file: Optional[UploadFile] = File(None),
    use_sample: bool = Query(False, description="Use bundled sample dataset"),
):
    """
    Upload a CSV/JSON dataset and start the sonification pipeline.
    
    - Upload a file: POST with multipart form data
    - Use sample data: POST with ?use_sample=true
    
    Returns a task_id for polling progress.
    """
    task_id = task_manager.create_task()

    if use_sample:
        # Run pipeline with bundled sample data
        asyncio.create_task(orchestrator.execute_with_sample(task_id))
        return UploadResponse(
            task_id=task_id,
            status="processing",
            message="Pipeline started with sample dataset",
        )

    if file is None:
        raise HTTPException(
            status_code=400,
            detail="Either upload a file or set use_sample=true",
        )

    # Validate file type
    filename = file.filename or "data.csv"
    if not filename.lower().endswith((".csv", ".json")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and JSON files are supported",
        )

    # Read file content
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Start pipeline in background
    asyncio.create_task(orchestrator.execute(task_id, content, filename))

    return UploadResponse(
        task_id=task_id,
        status="processing",
        message=f"Pipeline started with {filename}",
    )


@router.post("/generate")
async def generate_direct_pipeline(
    request: Request,
    file: Optional[UploadFile] = File(None),
    use_sample: bool = Form(False),
    use_archive: bool = Form(False),
    knock: bool = Form(False),
    start_year: int = Form(1968),
    end_year: int = Form(1975),
    region: str = Form("Vietnam USA"),
    threshold: str = Form("farewell"),
    mood: str = Form("tired_accepting"),
):
    """
    Direct frontend generation endpoint.
    Accepts one uploaded CSV/JSON file or the bundled sample dataset and returns
    events, embedding points, melody, metadata, and a downloadable MIDI URL.
    """
    if mood not in VALID_MOODS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Expected one of: {sorted(VALID_MOODS)}",
        )

    try:
        analysis_source = "uploaded_dataset_fields"
        query_meta = {}

        if use_archive or knock or (not use_sample and file is None):
            if knock:
                start_year = 1968
                end_year = 1975
                region = "Vietnam USA"
                threshold = "farewell"

            if start_year > end_year:
                raise HTTPException(status_code=400, detail="start_year must be before end_year")

            archive_events = archive_service.query_events(
                start_year=start_year,
                end_year=end_year,
                region=region,
                threshold=threshold,
            )
            analyzed_events, analysis_source = await analyzeEventsWithAI(archive_events, threshold)
            df = _archive_events_to_dataframe(analyzed_events)
            query_meta = {
                "mode": "archive",
                "startYear": start_year,
                "endYear": end_year,
                "region": region,
                "threshold": threshold,
                "selectedEvents": len(analyzed_events),
            }
        elif use_sample:
            sample_path = Path(settings.DATA_DIR) / "sample_vietnam_data.csv"
            df = ingestion.load_sample_data(str(sample_path))
            query_meta = {"mode": "sample"}
        else:
            if file is None:
                raise HTTPException(
                    status_code=400,
                    detail="Upload a CSV/JSON file, set use_sample=true, or use the archive query fields.",
                )

            filename = file.filename or "dataset.csv"
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            if filename.lower().endswith(".json"):
                df = ingestion.parse_json(content)
            elif filename.lower().endswith(".csv"):
                df = ingestion.parse_csv(content)
            else:
                raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
            query_meta = {"mode": "uploaded_file", "filename": filename}

        return await _generate_all_backend_soundscapes(
            df,
            request,
            mood,
            analysis_source=analysis_source,
            query_meta=query_meta,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/status/{task_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(task_id: str):
    """
    Poll the current status of a pipeline task.
    Frontend uses this to update the ProcessingSection progress steps.
    """
    task = task_manager.get_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return PipelineStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress_pct=task.progress_pct,
        current_step=task.current_step,
        total_steps=5,
        steps=task.get_steps(),
        error=task.error,
    )


@router.get("/result/{task_id}", response_model=PipelineResultResponse)
async def get_pipeline_result(task_id: str):
    """
    Retrieve the complete result of a finished pipeline task.
    Returns events with embedding coordinates, music metadata, and MIDI URL.
    """
    task = task_manager.get_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == PipelineStatusEnum.PROCESSING or task.status == PipelineStatusEnum.PENDING:
        raise HTTPException(status_code=202, detail="Pipeline still processing")

    if task.status == PipelineStatusEnum.FAILED:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {task.error}")

    if task.result is None:
        raise HTTPException(status_code=500, detail="Result is empty")

    return PipelineResultResponse(**task.result)
