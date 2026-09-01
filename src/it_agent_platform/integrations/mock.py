from typing import Any

from ..models import ProposedAction, utc_now
from .base import ActionExecutor


class MockExecutor(ActionExecutor):
    """Safe default adapter: records what would happen and causes no external effects."""

    async def execute(self, action: ProposedAction) -> dict[str, Any]:
        return {
            "mode": "mock",
            "operation": action.operation,
            "target": action.target,
            "idempotency_key": action.idempotency_key,
            "executed_at": utc_now().isoformat(),
        }
