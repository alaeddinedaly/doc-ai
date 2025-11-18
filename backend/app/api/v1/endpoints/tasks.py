"""Task status endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ....services.tasks import TaskTracker

router = APIRouter()
tracker = TaskTracker()


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str) -> dict:
    """Return task status."""

    data = tracker.get_progress(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": data.get("status", "unknown"),
        "current_step": int(data.get("current_step", 0)),
        "total_steps": int(data.get("total_steps", 0)),
        "message": data.get("message"),
        "result_id": data.get("result_id") or None,
    }

