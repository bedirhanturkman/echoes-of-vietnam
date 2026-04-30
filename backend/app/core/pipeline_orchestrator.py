"""
Pipeline Orchestrator.
Coordinates the full data sonification pipeline from ingestion to MIDI output.
"""

import asyncio
import numpy as np
from pathlib import Path

from app.services.data_ingestion import DataIngestionService
from app.services.embedding_service import EmbeddingService
from app.services.reduction_service import ReductionService
from app.services.mapping_service import MappingService
from app.services.music_service import MusicService
from app.services.llm_service import LLMService
from app.tasks.task_manager import task_manager
from app.models.schemas import (
    EventResult,
    MusicMetadata,
    PipelineResultResponse,
)


class PipelineOrchestrator:
    """
    Orchestrates the 5-step pipeline:
    1. Data Ingestion → Clean DataFrame
    2. Embedding Generation → 1536-d vectors
    3. Dimensionality Reduction → 2D coords + clusters
    4. Musical Mapping → Note sequences + metadata
    5. MIDI Generation → .mid file

    Each step updates the task manager for frontend progress tracking.
    """

    def __init__(self):
        self.ingestion = DataIngestionService()
        self.embedding = EmbeddingService()
        self.reduction = ReductionService()
        self.mapping = MappingService()
        self.music = MusicService()
        self.llm = LLMService()

    async def execute(self, task_id: str, file_content: bytes, filename: str):
        """
        Run the complete pipeline asynchronously.

        Args:
            task_id: Task identifier for progress tracking
            file_content: Raw file bytes (CSV or JSON)
            filename: Original filename for format detection
        """
        try:
            # =====================================================
            # STEP 1: Data Ingestion
            # =====================================================
            task_manager.update_step(task_id, 0)
            await asyncio.sleep(0.5)  # Small delay for UI visibility

            if filename.lower().endswith(".json"):
                df = self.ingestion.parse_json(file_content)
            else:
                df = self.ingestion.parse_csv(file_content)

            print(f"[DATA] Step 1 complete: {len(df)} records loaded")

            # =====================================================
            # STEP 2: Embedding Generation
            # =====================================================
            task_manager.update_step(task_id, 1)
            await asyncio.sleep(0.3)

            titles = df["title"].tolist()
            metadata_list = df.apply(
                lambda row: {
                    "date": row.get("date_str", ""),
                    "location": row.get("location", "Unknown"),
                    "category": row.get("category", "uncertainty"),
                    "sentiment": row.get("sentiment", 0.0),
                },
                axis=1,
            ).tolist()

            embeddings = await self.embedding.generate_embeddings(titles, metadata_list)
            print(f"[EMB] Step 2 complete: {embeddings.shape} embeddings generated")

            # =====================================================
            # STEP 3: Dimensionality Reduction + Clustering
            # =====================================================
            task_manager.update_step(task_id, 2)
            await asyncio.sleep(0.3)

            coords_2d = self.reduction.reduce_to_2d(embeddings)
            categories = df["category"].tolist()
            clusters = self.reduction.cluster_embeddings(embeddings, categories)

            print(f"[DIM] Step 3 complete: {len(set(clusters))} clusters found")

            # =====================================================
            # STEP 4: Musical Mapping
            # =====================================================
            task_manager.update_step(task_id, 3)
            await asyncio.sleep(0.3)
            print(">> STEP 4: Mapping start")

            # Build full metadata for mapping
            full_metadata = []
            for i, row in df.iterrows():
                full_metadata.append({
                    "id": f"e{i+1}",
                    "date": row.get("date_str", ""),
                    "title": row.get("title", ""),
                    "category": row.get("category", "uncertainty"),
                    "sentiment": row.get("sentiment", 0.0),
                    "casualties": row.get("casualties", 0),
                    "location": row.get("location", "Unknown"),
                })

            mapping_result = self.mapping.map_data_to_music(
                coords_2d, clusters, full_metadata
            )
            print(f"[MAP] Step 4 complete: {len(mapping_result.notes)} notes mapped")
            
            # --- AI Interpretation (GPT-4o-mini) ---
            print(">> STEP 4: LLM start")
            llm_result = await self.llm.generate_interpretations(full_metadata, mapping_result)
            print(">> STEP 4: LLM end")
            global_interpretation = llm_result.get("global_interpretation", "")
            event_interpretations = llm_result.get("events", {})
            print("[LLM] Interpretations generated successfully")

            # =====================================================
            # STEP 5: MIDI Generation
            # =====================================================
            task_manager.update_step(task_id, 4)
            await asyncio.sleep(0.3)

            midi_url = self.music.generate_midi(mapping_result, task_id)
            duration_seconds = self.music.get_duration_seconds(mapping_result)

            print(f"[MIDI] Step 5 complete: MIDI saved -> {midi_url}")

            # =====================================================
            # Assemble final result
            # =====================================================
            events = []
            for i, (coord, meta) in enumerate(zip(coords_2d, full_metadata)):
                event_id = meta["id"]
                
                # Get dynamic interpretation from LLM result, fallback to mapping template
                interpretation = event_interpretations.get(
                    event_id, 
                    mapping_result.interpretations.get(event_id, "A musical passage derived from historical data.")
                )
                
                events.append(EventResult(
                    id=event_id,
                    date=meta["date"],
                    title=meta["title"],
                    category=meta["category"],
                    sentiment=meta["sentiment"],
                    x=round(float(coord[0]), 1),
                    y=round(float(coord[1]), 1),
                    musicalInterpretation=interpretation,
                ))

            # Build music metadata
            chord_str = " - ".join(mapping_result.progression.get("chords", []))
            music_metadata = MusicMetadata(
                tempo_bpm=mapping_result.tempo,
                scale=list(mapping_result.scale.keys())[0] if isinstance(mapping_result.scale, dict) and "name" in mapping_result.scale else "pentatonic",
                scale_name=mapping_result.scale.get("name", "Pentatonic"),
                chord_progression=chord_str,
                progression_name=mapping_result.progression.get("name", "Dylan Progression"),
                mood=mapping_result.mood,
                total_notes=len(mapping_result.notes),
                duration_seconds=round(duration_seconds, 1),
            )

            playback_notes = [
                {
                    "pitch": note.pitch,
                    "velocity": note.velocity,
                    "start_time": note.start_time,
                    "duration": note.duration,
                }
                for note in mapping_result.notes
            ]

            # Overall interpretation text (LLM generated)
            interpretation_text = global_interpretation if global_interpretation else (
                f"This composition is generated from {len(events)} clustered Vietnam War records "
                f"spanning {events[0].date if events else '?'} to {events[-1].date if events else '?'}. "
                f"The overall mood is {mapping_result.mood}. "
                f"Conflict-heavy clusters produce darker tones and heavier durations, "
                f"while peace-related clusters move toward softer, more stable harmonic structures. "
                f"The piece unfolds at {mapping_result.tempo} BPM using a "
                f"{mapping_result.scale.get('name', 'pentatonic')} scale with "
                f"{chord_str} chord progressions inspired by Bob Dylan."
            )

            result = PipelineResultResponse(
                task_id=task_id,
                events=events,
                music_metadata=music_metadata,
                midi_url=midi_url,
                playback_notes=playback_notes,
                interpretation_text=interpretation_text,
            )

            task_manager.complete_task(task_id, result.model_dump())
            print(f"[OK] Pipeline complete for task {task_id[:8]}")

        except Exception as e:
            print(f"[FAIL] Pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
            task_manager.fail_task(task_id, str(e))

    async def execute_with_sample(self, task_id: str):
        """
        Execute the pipeline using the bundled sample dataset.
        """
        sample_path = Path("data/sample_vietnam_data.csv")
        if not sample_path.exists():
            task_manager.fail_task(task_id, "Sample dataset not found")
            return

        with open(sample_path, "rb") as f:
            content = f.read()

        await self.execute(task_id, content, "sample_vietnam_data.csv")
