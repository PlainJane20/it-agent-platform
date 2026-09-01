import asyncio
from uuid import uuid4

from ..audit import AuditLog
from ..models import WorkflowResult, WorkRequest
from ..policy import ApprovalPolicy
from .base import SpecialistAgent, includes


class Coordinator:
    def __init__(
        self,
        agents: dict[str, SpecialistAgent],
        policy: ApprovalPolicy,
        audit: AuditLog,
    ) -> None:
        self.agents = agents
        self.policy = policy
        self.audit = audit

    def route(self, request: WorkRequest) -> list[str]:
        selected = ["triage"]
        rules = {
            "identity": ("access", "account", "onboard", "offboard", "password", "mfa"),
            "incident": ("incident", "outage", "phish", "malware", "breach", "compromised"),
            "endpoint": ("device", "laptop", "endpoint", "patch", "intune", "jamf"),
            "compliance": ("audit", "evidence", "control", "compliance", "sox", "soc 2"),
            "knowledge": ("repeat", "runbook", "knowledge", "documentation"),
        }
        for agent, terms in rules.items():
            if includes(request, *terms):
                selected.append(agent)
        return list(dict.fromkeys(selected))

    async def run(self, request: WorkRequest) -> WorkflowResult:
        workflow_id = str(uuid4())
        route = self.route(request)
        self.audit.record(
            workflow_id, "workflow_started", request.requester, {"request": request.model_dump()}
        )
        findings = await asyncio.gather(
            *(self.agents[name].analyze(workflow_id, request) for name in route)
        )
        actions = [action for finding in findings for action in finding.actions]
        for action in actions:
            decision = self.policy.evaluate(action)
            action.status = decision.status
            self.audit.record(
                workflow_id,
                "action_policy_evaluated",
                "policy-engine",
                {"action": action.model_dump(), "reason": decision.reason},
            )
        result = WorkflowResult(
            workflow_id=workflow_id,
            request=request,
            route=route,
            findings=findings,
            actions=actions,
            summary=f"{len(findings)} specialists returned {len(actions)} proposed actions.",
        )
        self.audit.record(
            workflow_id, "workflow_analyzed", "coordinator", {"result": result.model_dump()}
        )
        return result
