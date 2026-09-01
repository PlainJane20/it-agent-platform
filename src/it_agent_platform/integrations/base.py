from abc import ABC, abstractmethod
from typing import Any

from ..models import ProposedAction


class ActionExecutor(ABC):
    @abstractmethod
    async def execute(self, action: ProposedAction) -> dict[str, Any]:
        raise NotImplementedError
