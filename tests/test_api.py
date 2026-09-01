from pathlib import Path

from fastapi.testclient import TestClient

import it_agent_platform.api as api_module
from it_agent_platform.config import Settings


def test_api_workflow_approval_and_audit(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        api_module,
        "get_settings",
        lambda: Settings(it_agent_db_path=tmp_path / "api-audit.db"),
    )
    with TestClient(api_module.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post(
            "/v1/workflows",
            json={
                "requester": "alex@example.com",
                "title": "VPN unavailable",
                "description": "VPN is down for the finance team",
            },
        )
        assert response.status_code == 200
        workflow = response.json()
        action = next(item for item in workflow["actions"] if item["status"] == "approval_required")

        assert client.post(f"/v1/actions/{action['id']}/execute").status_code == 401
        mismatch = client.post(
            f"/v1/actions/{action['id']}/approve",
            headers={"X-Actor": "other@example.com"},
            json={"approver": "lead@example.com", "reason": "reviewed"},
        )
        assert mismatch.status_code == 403

        approved = client.post(
            f"/v1/actions/{action['id']}/approve",
            headers={"X-Actor": "lead@example.com"},
            json={"approver": "lead@example.com", "reason": "reviewed"},
        )
        assert approved.status_code == 200
        executed = client.post(
            f"/v1/actions/{action['id']}/execute",
            headers={"X-Actor": "lead@example.com"},
        )
        assert executed.json()["mode"] == "mock"

        audit = client.get(
            f"/v1/workflows/{workflow['workflow_id']}/audit",
            headers={"X-Actor": "auditor@example.com"},
        )
        event_types = [event["event_type"] for event in audit.json()["events"]]
        assert "action_approved" in event_types
        assert "action_executed" in event_types
