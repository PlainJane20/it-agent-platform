from __future__ import annotations

from typing import Optional

from openai import AsyncOpenAI

from .agents import (
    ComplianceAgent,
    Coordinator,
    EndpointAgent,
    IdentityAgent,
    IncidentAgent,
    KnowledgeAgent,
    OpenAISpecialistAgent,
    TriageAgent,
)
from .audit import AuditLog
from .config import Settings
from .integrations import ActionExecutor, MockExecutor
from .models import ActionStatus, ApprovalDecision, ProposedAction, WorkflowResult, WorkRequest
from .policy import ApprovalPolicy


class AutomationService:
    def __init__(self, settings: Settings, executor: Optional[ActionExecutor] = None) -> None:
        self.settings = settings
        self.audit = AuditLog(settings.it_agent_db_path)
        self.executor = executor or MockExecutor()
        specialists = [
            TriageAgent(),
            IdentityAgent(),
            IncidentAgent(),
            EndpointAgent(),
            KnowledgeAgent(),
            ComplianceAgent(),
        ]
        if settings.it_agent_analysis_mode == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when analysis mode is openai")
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            specialists = [
                OpenAISpecialistAgent(agent, client, settings.openai_model) for agent in specialists
            ]
        self.coordinator = Coordinator(
            {agent.name: agent for agent in specialists}, ApprovalPolicy(), self.audit
        )
        self.actions: dict[str, ProposedAction] = {}

    async def submit(self, request: WorkRequest) -> WorkflowResult:
        result = await self.coordinator.run(request)
        self.actions.update({action.id: action for action in result.actions})
        return result

    def approve(self, action_id: str, decision: ApprovalDecision) -> ProposedAction:
        action = self._get_action(action_id)
        if action.status != ActionStatus.APPROVAL_REQUIRED:
            raise ValueError(f"action cannot be approved from status {action.status}")
        action.status = ActionStatus.APPROVED
        self.audit.record(
            action.workflow_id,
            "action_approved",
            decision.approver,
            {"action_id": action.id, "reason": decision.reason},
        )
        return action

    async def execute(self, action_id: str, actor: str) -> dict:
        action = self._get_action(action_id)
        if action.status != ActionStatus.APPROVED:
            raise PermissionError("action must be approved before execution")
        result = await self.executor.execute(action)
        action.status = ActionStatus.EXECUTED
        self.audit.record(
            action.workflow_id,
            "action_executed",
            actor,
            {"action": action.model_dump(), "result": result},
        )
        return result

    def _get_action(self, action_id: str) -> ProposedAction:
        try:
            return self.actions[action_id]
        except KeyError as error:
            raise KeyError(f"unknown action: {action_id}") from error
