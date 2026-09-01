from types import SimpleNamespace

import pytest

from it_agent_platform.agents.openai_agent import (
    LLMActionProposal,
    LLMAssessment,
    OpenAISpecialistAgent,
)
from it_agent_platform.agents.specialists import TriageAgent
from it_agent_platform.models import ActionKind, RiskLevel, WorkRequest


class FakeResponses:
    def __init__(self, assessment):
        self.assessment = assessment

    async def parse(self, **kwargs):
        assert kwargs["store"] is False
        assert kwargs["text_format"] is LLMAssessment
        return SimpleNamespace(output_parsed=self.assessment)


class FakeClient:
    def __init__(self, assessment):
        self.responses = FakeResponses(assessment)


@pytest.mark.asyncio
async def test_openai_specialist_enforces_operation_allowlist():
    assessment = LLMAssessment(
        summary="Route the outage.",
        confidence=0.9,
        evidence=["The request says the service is down."],
        actions=[
            LLMActionProposal(
                kind=ActionKind.EXTERNAL_WRITE,
                operation="create_or_update_ticket",
                target="service-desk",
                rationale="Create the reviewed ticket.",
                risk=RiskLevel.MEDIUM,
            ),
            LLMActionProposal(
                kind=ActionKind.PRIVILEGED,
                operation="invented_admin_operation",
                target="production",
                rationale="This must be discarded.",
                risk=RiskLevel.CRITICAL,
            ),
        ],
    )
    agent = OpenAISpecialistAgent(TriageAgent(), FakeClient(assessment), "test-model")
    finding = await agent.analyze(
        "workflow-1",
        WorkRequest(
            requester="alex@example.com",
            title="VPN down",
            description="The VPN is unavailable.",
        ),
    )
    assert [action.operation for action in finding.actions] == ["create_or_update_ticket"]
    assert finding.actions[0].idempotency_key
