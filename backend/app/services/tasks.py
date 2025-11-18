"""Task utilities for progress tracking."""

from __future__ import annotations

import redis

from ..core.config import settings


class TaskTracker:
    """Persists task progress in Redis."""

    def __init__(self) -> None:
        self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def set_progress(
        self,
        task_id: str,
        *,
        status: str,
        current_step: int,
        total_steps: int,
        message: str | None = None,
        result_id: str | None = None,
    ) -> None:
        payload = {
            "status": status,
            "current_step": current_step,
            "total_steps": total_steps,
            "message": message or "",
            "result_id": result_id or "",
        }
        self.client.hset(f"task:{task_id}", mapping=payload)
        self.client.expire(f"task:{task_id}", 3600)

    def get_progress(self, task_id: str) -> dict[str, str]:
        return self.client.hgetall(f"task:{task_id}") or {}

