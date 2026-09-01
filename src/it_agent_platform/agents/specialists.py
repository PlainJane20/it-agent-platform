import hashlib

from ..models import (
    ActionKind,
    AgentFinding,
    Evidence,
    ProposedAction,
    RiskLevel,
    WorkRequest,
)
from .base import SpecialistAgent, includes


def key(workflow_id: str, operation: str, target: str) -> str:
    value = f"{workflow_id}:{operation}:{target}".encode()
    return hashlib.sha256(value).hexdigest()[:24]


class TriageAgent(SpecialistAgent):
    name = "triage"
    description = "Classifies, prioritizes, enriches, and routes service-desk requests."

    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        security = includes(request, "phish", "malware", "breach", "compromised")
        outage = includes(request, "outage", "down", "unavailable", "cannot access")
        priority = "P1" if security or outage else "P3"
        queue = "security" if security else "service-desk"
        action = ProposedAction(
            workflow_id=workflow_id,
            agent=self.name,
            kind=ActionKind.EXTERNAL_WRITE,
            operation="create_or_update_ticket",
            target=queue,
            arguments={"priority": priority, "title": request.title},
            rationale="Route the enriched request to the accountable support queue.",
            risk=RiskLevel.MEDIUM,
            idempotency_key=key(workflow_id, "create_or_update_ticket", queue),
        )
        return AgentFinding(
            agent=self.name,
            summary=f"Classified as {priority}; recommended queue: {queue}.",
            confidence=0.86,
            evidence=[Evidence(source="request", detail="Classification based on submitted text.")],
            actions=[action],
        )


class IdentityAgent(SpecialistAgent):
    name = "identity"
    description = "Reviews identity, access, onboarding, offboarding, and account requests."

    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        disable = includes(request, "terminate", "offboard", "disable account")
        operation = "disable_identity" if disable else "prepare_access_review"
        kind = ActionKind.PRIVILEGED if disable else ActionKind.DRAFT
        risk = RiskLevel.HIGH if disable else RiskLevel.LOW
        action = ProposedAction(
            workflow_id=workflow_id,
            agent=self.name,
            kind=kind,
            operation=operation,
            target=request.metadata.get("user", "unresolved-user"),
            arguments={"requester": request.requester},
            rationale="Apply the least-privilege identity workflow after ownership verification.",
            risk=risk,
            idempotency_key=key(workflow_id, operation, request.metadata.get("user", "unknown")),
        )
        return AgentFinding(
            agent=self.name,
            summary="Identity request identified; owner and target must be verified.",
            confidence=0.78,
            evidence=[Evidence(source="request", detail="Identity-related terms detected.")],
            actions=[action],
        )


class IncidentAgent(SpecialistAgent):
    name = "incident"
    description = "Builds incident timelines and proposes containment and recovery steps."

    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        action = ProposedAction(
            workflow_id=workflow_id,
            agent=self.name,
            kind=ActionKind.DRAFT,
            operation="draft_incident_timeline",
            target=request.id,
            rationale="Create a reviewable incident record before containment decisions.",
            risk=RiskLevel.LOW,
            idempotency_key=key(workflow_id, "draft_incident_timeline", request.id),
        )
        return AgentFinding(
            agent=self.name,
            summary="Potential incident detected; timeline and evidence preservation recommended.",
            confidence=0.82,
            evidence=[Evidence(source="request", detail="Incident indicators detected.")],
            actions=[action],
        )


class EndpointAgent(SpecialistAgent):
    name = "endpoint"
    description = "Reviews endpoint health, patching, device compliance, and remediation."

    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        target = request.metadata.get("device", "unresolved-device")
        action = ProposedAction(
            workflow_id=workflow_id,
            agent=self.name,
            kind=ActionKind.EXTERNAL_WRITE,
            operation="schedule_endpoint_remediation",
            target=target,
            rationale="Schedule remediation in the approved maintenance window.",
            risk=RiskLevel.MEDIUM,
            idempotency_key=key(workflow_id, "schedule_endpoint_remediation", target),
        )
        return AgentFinding(
            agent=self.name,
            summary="Endpoint remediation may be required; device identity must be confirmed.",
            confidence=0.76,
            evidence=[Evidence(source="request", detail="Endpoint or patch terms detected.")],
            actions=[action],
        )


class KnowledgeAgent(SpecialistAgent):
    name = "knowledge"
    description = "Drafts runbook and knowledge-base improvements."

    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        action = ProposedAction(
            workflow_id=workflow_id,
            agent=self.name,
            kind=ActionKind.DRAFT,
            operation="draft_knowledge_article",
            target=request.title,
            rationale="Capture reusable resolution guidance for human review.",
            risk=RiskLevel.LOW,
            idempotency_key=key(workflow_id, "draft_knowledge_article", request.title),
        )
        return AgentFinding(
            agent=self.name,
            summary="A draft knowledge article can be prepared after resolution.",
            confidence=0.7,
            actions=[action],
        )


class ComplianceAgent(SpecialistAgent):
    name = "compliance"
    description = "Identifies evidence needs and control implications."

    async def analyze(self, workflow_id: str, request: WorkRequest) -> AgentFinding:
        action = ProposedAction(
            workflow_id=workflow_id,
            agent=self.name,
            kind=ActionKind.DRAFT,
            operation="prepare_control_evidence_checklist",
            target=request.id,
            rationale="Preserve evidence without changing production systems.",
            risk=RiskLevel.LOW,
            idempotency_key=key(workflow_id, "prepare_control_evidence_checklist", request.id),
        )
        return AgentFinding(
            agent=self.name,
            summary="Control evidence checklist recommended.",
            confidence=0.74,
            actions=[action],
        )
