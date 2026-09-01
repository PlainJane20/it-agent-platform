from abc import ABC, abstractmethod

from ..models import AgentFinding, WorkRequest


class SpecialistAgent(ABC):
    name: str
    description: str

    @abstractmethod
    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        raise NotImplementedError


def includes(request: WorkRequest, *terms: str) -> bool:
    text = f"{request.title} {request.description}".lower()
    return any(term in text for term in terms)
