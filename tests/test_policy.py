from it_agent_platform.models import ActionKind, ProposedAction, RiskLevel
from it_agent_platform.policy import ApprovalPolicy


def action(
    kind: ActionKind, risk: RiskLevel = RiskLevel.LOW, operation: str = "prepare_access_review"
) -> ProposedAction:
    return ProposedAction(
        workflow_id="wf",
        agent="test",
        kind=kind,
        operation=operation,
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


def test_mislabelled_destructive_operation_still_requires_approval():
    # Model claims a privileged operation is a low-risk draft.
    decision = ApprovalPolicy().evaluate(
        action(ActionKind.DRAFT, RiskLevel.LOW, operation="disable_identity")
    )
    assert decision.status == "approval_required"
    assert "floor" in decision.reason


def test_destructive_label_is_never_lowered_by_table():
    decision = ApprovalPolicy().evaluate(
        action(ActionKind.DESTRUCTIVE, RiskLevel.LOW, operation="prepare_access_review")
    )
    assert decision.status == "approval_required"


def test_unknown_operation_fails_closed():
    decision = ApprovalPolicy().evaluate(
        action(ActionKind.DRAFT, RiskLevel.LOW, operation="wipe_all_devices")
    )
    assert decision.status == "approval_required"
    assert "unknown operation" in decision.reason


def test_floor_table_covers_every_allowed_operation():
    from it_agent_platform.agents.openai_agent import ALLOWED_OPERATIONS
    from it_agent_platform.policy import OPERATION_FLOORS

    allowed = set().union(*ALLOWED_OPERATIONS.values())
    assert allowed <= set(OPERATION_FLOORS)
