from dataclasses import dataclass

from .models import ActionKind, ActionStatus, ProposedAction, RiskLevel


@dataclass(frozen=True)
class PolicyDecision:
    status: ActionStatus
    reason: str


class ApprovalPolicy:
    """Central, deterministic policy. Model output never overrides this layer."""

    _approval_kinds = {
        ActionKind.EXTERNAL_WRITE,
        ActionKind.PRIVILEGED,
        ActionKind.DESTRUCTIVE,
    }

    def evaluate(self, action: ProposedAction) -> PolicyDecision:
        if action.kind in self._approval_kinds:
            return PolicyDecision(
                ActionStatus.APPROVAL_REQUIRED,
                f"{action.kind.value} actions require human approval",
            )
        if action.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return PolicyDecision(
                ActionStatus.APPROVAL_REQUIRED,
                f"{action.risk.value} risk actions require human approval",
            )
        return PolicyDecision(ActionStatus.APPROVED, "safe, reversible local action")
