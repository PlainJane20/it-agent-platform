from pathlib import Path

import pytest

from it_agent_platform.config import Settings
from it_agent_platform.models import ActionStatus, ApprovalDecision, WorkRequest
from it_agent_platform.service import AutomationService


@pytest.fixture
def service(tmp_path: Path) -> AutomationService:
    return AutomationService(Settings(it_agent_db_path=tmp_path / "audit.db"))


@pytest.mark.asyncio
async def test_routes_identity_and_requires_approval(service: AutomationService):
    result = await service.submit(
        WorkRequest(
            requester="manager@example.com",
            title="Offboard employee",
            description="Terminate access and disable account",
            metadata={"user": "employee@example.com"},
        )
    )
    assert result.route == ["triage", "identity"]
    privileged = next(action for action in result.actions if action.kind == "privileged")
    assert privileged.status == ActionStatus.APPROVAL_REQUIRED


@pytest.mark.asyncio
async def test_action_cannot_execute_without_approval(service: AutomationService):
    result = await service.submit(
        WorkRequest(requester="u@example.com", title="Laptop down", description="Device is down")
    )
    action = next(item for item in result.actions if item.status == "approval_required")
    with pytest.raises(PermissionError):
        await service.execute(action.id, "operator@example.com")


@pytest.mark.asyncio
async def test_approved_action_executes_in_mock_mode(service: AutomationService):
    result = await service.submit(
        WorkRequest(requester="u@example.com", title="VPN unavailable", description="VPN is down")
    )
    action = next(item for item in result.actions if item.status == "approval_required")
    service.approve(
        action.id,
        ApprovalDecision(approver="lead@example.com", reason="Ticket creation reviewed"),
    )
    execution = await service.execute(action.id, "lead@example.com")
    assert execution["mode"] == "mock"
    assert action.status == ActionStatus.EXECUTED
