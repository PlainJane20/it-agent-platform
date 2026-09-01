from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status

from .config import get_settings
from .models import ApprovalDecision, WorkflowResult, WorkRequest
from .service import AutomationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = AutomationService(get_settings())
    yield


app = FastAPI(
    title="IT Agent Platform",
    version="0.1.0",
    description="Approval-first multi-agent automation for IT operations.",
    lifespan=lifespan,
)


def get_service() -> AutomationService:
    return app.state.service


def require_actor(x_actor: Annotated[Optional[str], Header()] = None) -> str:
    if not x_actor:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "X-Actor header is required")
    return x_actor


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/workflows", response_model=WorkflowResult)
async def submit_workflow(
    request: WorkRequest,
    service: Annotated[AutomationService, Depends(get_service)],
) -> WorkflowResult:
    return await service.submit(request)


@app.post("/v1/actions/{action_id}/approve")
def approve_action(
    action_id: str,
    decision: ApprovalDecision,
    actor: Annotated[str, Depends(require_actor)],
    service: Annotated[AutomationService, Depends(get_service)],
):
    if actor != decision.approver:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "actor must match approver")
    try:
        return service.approve(action_id, decision)
    except (KeyError, ValueError) as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error


@app.post("/v1/actions/{action_id}/execute")
async def execute_action(
    action_id: str,
    actor: Annotated[str, Depends(require_actor)],
    service: Annotated[AutomationService, Depends(get_service)],
):
    try:
        return await service.execute(action_id, actor)
    except KeyError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except PermissionError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error)) from error


@app.get("/v1/workflows/{workflow_id}/audit")
def workflow_audit(
    workflow_id: str,
    _: Annotated[str, Depends(require_actor)],
    service: Annotated[AutomationService, Depends(get_service)],
):
    return {"events": service.audit.list_events(workflow_id)}


def run() -> None:
    uvicorn.run("it_agent_platform.api:app", host="0.0.0.0", port=8000, reload=False)
