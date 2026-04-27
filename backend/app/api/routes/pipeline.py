"""
Pipeline API endpoints.
Handles file upload, pipeline status polling, and result retrieval.
"""

import asyncio
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Query

from app.tasks.task_manager import task_manager
from app.core.pipeline_orchestrator import PipelineOrchestrator
from app.models.schemas import (
    UploadResponse,
    PipelineStatusResponse,
    PipelineResultResponse,
    PipelineStatusEnum,
)

router = APIRouter()
orchestrator = PipelineOrchestrator()


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
