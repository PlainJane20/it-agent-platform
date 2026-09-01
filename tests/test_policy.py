from it_agent_platform.models import ActionKind, ProposedAction, RiskLevel
from it_agent_platform.policy import ApprovalPolicy


def action(kind: ActionKind, risk: RiskLevel = RiskLevel.LOW) -> ProposedAction:
    return ProposedAction(
        workflow_id="wf",
        agent="test",
        kind=kind,
        operation="test",
        target="target",
        rationale="test",
        risk=risk,
        idempotency_key="key",
    )


def test_external_write_requires_approval():
    decision = ApprovalPolicy().evaluate(action(ActionKind.EXTERNAL_WRITE))
    assert decision.status == "approval_required"


def test_low_risk_draft_is_automatically_approved():
    decision = ApprovalPolicy().evaluate(action(ActionKind.DRAFT))
    assert decision.status == "approved"


def test_high_risk_read_still_requires_approval():
    decision = ApprovalPolicy().evaluate(action(ActionKind.READ, RiskLevel.HIGH))
    assert decision.status == "approval_required"
