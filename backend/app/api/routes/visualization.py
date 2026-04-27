"""
Visualization API endpoints.
Provides embedding data in a format suitable for frontend charting.
"""

from fastapi import APIRouter, HTTPException

from app.tasks.task_manager import task_manager
from app.models.schemas import PipelineStatusEnum

router = APIRouter()


@router.get("/embedding/{task_id}")
async def get_embedding_data(task_id: str):
    """
    Retrieve embedding visualization data for a completed task.
    Returns the events array formatted for the EmbeddingMap component.
    """
    task = task_manager.get_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != PipelineStatusEnum.COMPLETED:
        raise HTTPException(status_code=202, detail="Pipeline not yet completed")

    if task.result is None:
        raise HTTPException(status_code=500, detail="No result data available")

    # Return just the events array for the scatter chart
    events = task.result.get("events", [])

    # Group by category for legend
    categories = {}
    for event in events:
        cat = event["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    return {
        "task_id": task_id,
        "total_events": len(events),
        "events": events,
        "category_counts": categories,
    }
