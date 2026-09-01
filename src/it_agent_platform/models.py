from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionKind(str, Enum):
    READ = "read"
    DRAFT = "draft"
    EXTERNAL_WRITE = "external_write"
    PRIVILEGED = "privileged"
    DESTRUCTIVE = "destructive"


class ActionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED = "approved"
    EXECUTED = "executed"
    REJECTED = "rejected"
    FAILED = "failed"


class WorkRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str = "api"
    requester: str
    title: str
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class Evidence(BaseModel):
    source: str
    detail: str


class ProposedAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    agent: str
    kind: ActionKind
    operation: str
    target: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    risk: RiskLevel
    status: ActionStatus = ActionStatus.PROPOSED
    idempotency_key: str
    created_at: datetime = Field(default_factory=utc_now)


class AgentFinding(BaseModel):
    agent: str
    summary: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)
    actions: list[ProposedAction] = Field(default_factory=list)


class WorkflowResult(BaseModel):
    workflow_id: str
    request: WorkRequest
    route: list[str]
    findings: list[AgentFinding]
    actions: list[ProposedAction]
    summary: str
    created_at: datetime = Field(default_factory=utc_now)


class ApprovalDecision(BaseModel):
    approver: str
    reason: str
