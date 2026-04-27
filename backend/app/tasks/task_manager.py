"""
In-memory async task manager.
Tracks pipeline execution status for polling by the frontend.
Replaces Redis/Celery with a simpler approach suitable for academic projects.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.models.schemas import PipelineStep, PipelineStatusEnum


# ---------------------------------------------------------------------------
# Pipeline step definitions
# ---------------------------------------------------------------------------

PIPELINE_STEPS = [
    {"name": "data_ingestion", "description": "Reading historical fragments..."},
    {"name": "embedding", "description": "Creating semantic embeddings..."},
    {"name": "reduction", "description": "Mapping memories into coordinates..."},
    {"name": "mapping", "description": "Translating data into notes..."},
    {"name": "generation", "description": "Generating the final soundscape..."},
]


class TaskState:
    """Represents the state of a single pipeline task."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status: PipelineStatusEnum = PipelineStatusEnum.PENDING
        self.current_step: int = 0
        self.error: Optional[str] = None
        self.result: Optional[dict] = None
        self.created_at: datetime = datetime.utcnow()

    @property
    def progress_pct(self) -> int:
        if self.status == PipelineStatusEnum.COMPLETED:
            return 100
        if self.status == PipelineStatusEnum.FAILED:
            return 0
        total = len(PIPELINE_STEPS)
        return int((self.current_step / total) * 100)

    def get_steps(self) -> list[PipelineStep]:
        steps = []
        for i, step_def in enumerate(PIPELINE_STEPS):
            if i < self.current_step:
                status = "completed"
            elif i == self.current_step and self.status == PipelineStatusEnum.PROCESSING:
                status = "active"
            else:
                status = "pending"
            steps.append(PipelineStep(
                name=step_def["name"],
                status=status,
                description=step_def["description"],
            ))
        return steps


class TaskManager:
    """
    Singleton task manager storing pipeline states in memory.
    Thread-safe for single-worker uvicorn usage.
    """

    def __init__(self):
        self._tasks: dict[str, TaskState] = {}

    def create_task(self) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = TaskState(task_id)
        return task_id

    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)

    def update_step(self, task_id: str, step: int):
        """Update the current pipeline step."""
        task = self._tasks.get(task_id)
        if task:
            task.current_step = step
            task.status = PipelineStatusEnum.PROCESSING

    def complete_task(self, task_id: str, result: dict):
        """Mark a task as completed with its result."""
        task = self._tasks.get(task_id)
        if task:
            task.status = PipelineStatusEnum.COMPLETED
            task.current_step = len(PIPELINE_STEPS)
            task.result = result

    def fail_task(self, task_id: str, error: str):
        """Mark a task as failed."""
        task = self._tasks.get(task_id)
        if task:
            task.status = PipelineStatusEnum.FAILED
            task.error = error


# Singleton instance
task_manager = TaskManager()
