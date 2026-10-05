from dataclasses import dataclass

from .models import ActionKind, ActionStatus, ProposedAction, RiskLevel


@dataclass(frozen=True)
class PolicyDecision:
    status: ActionStatus
    reason: str


_KIND_ORDER = [
    ActionKind.READ,
    ActionKind.DRAFT,
    ActionKind.EXTERNAL_WRITE,
    ActionKind.PRIVILEGED,
    ActionKind.DESTRUCTIVE,
]
_RISK_ORDER = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

# Minimum (kind, risk) per operation, owned by the platform rather than the model.
# Operations absent from this table are unknown and always require approval.
OPERATION_FLOORS: dict[str, tuple[ActionKind, RiskLevel]] = {
    "create_or_update_ticket": (ActionKind.EXTERNAL_WRITE, RiskLevel.MEDIUM),
    "prepare_access_review": (ActionKind.DRAFT, RiskLevel.LOW),
    "disable_identity": (ActionKind.PRIVILEGED, RiskLevel.HIGH),
    "draft_incident_timeline": (ActionKind.DRAFT, RiskLevel.LOW),
    "schedule_endpoint_remediation": (ActionKind.EXTERNAL_WRITE, RiskLevel.MEDIUM),
    "draft_knowledge_article": (ActionKind.DRAFT, RiskLevel.LOW),
    "prepare_control_evidence_checklist": (ActionKind.DRAFT, RiskLevel.LOW),
}


def _stricter(a, b, order):
    return a if order.index(a) >= order.index(b) else b


class ApprovalPolicy:
    """Central, deterministic policy. Model output never overrides this layer."""

    _approval_kinds = {
        ActionKind.EXTERNAL_WRITE,
        ActionKind.PRIVILEGED,
        ActionKind.DESTRUCTIVE,
    }

    def evaluate(self, action: ProposedAction) -> PolicyDecision:
        floor = OPERATION_FLOORS.get(action.operation)
        if floor is None:
            return PolicyDecision(
                ActionStatus.APPROVAL_REQUIRED,
                f"unknown operation '{action.operation}' requires human approval",
            )
        kind = _stricter(action.kind, floor[0], _KIND_ORDER)
        risk = _stricter(action.risk, floor[1], _RISK_ORDER)
        raised = kind != action.kind or risk != action.risk
        note = " (raised from model label by operation floor)" if raised else ""
        if kind in self._approval_kinds:
            return PolicyDecision(
                ActionStatus.APPROVAL_REQUIRED,
                f"{kind.value} actions require human approval{note}",
            )
        if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return PolicyDecision(
                ActionStatus.APPROVAL_REQUIRED,
                f"{risk.value} risk actions require human approval{note}",
            )
        return PolicyDecision(ActionStatus.APPROVED, "safe, reversible local action")
