# IT Agent Platform

An approval-first starter platform for automating IT operations with a coordinator and six
specialist agents. It ships in **mock mode**, so it produces no external side effects until you
add and explicitly enable a production connector.

## What it does

- Routes incoming work to triage, identity, incident, endpoint, knowledge, and compliance agents
- Runs independent specialist analysis concurrently
- Converts recommendations into typed, idempotent proposed actions
- Requires human approval for external writes, privileged, destructive, or high-risk actions
- Records workflows, policy decisions, approvals, and executions in SQLite
- Exposes a FastAPI API and includes tests, CI, a Dockerfile, and a threat model

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
pytest
uvicorn it_agent_platform.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API.

Submit the included service request:

```bash
curl -s http://127.0.0.1:8000/v1/workflows \
  -H 'Content-Type: application/json' \
  --data @examples/service_request.json
```

External ticket creation will be returned as `approval_required`. Approve it with an identified
actor, then execute it. In the default configuration, execution only returns a mock receipt.

```bash
curl -s -X POST http://127.0.0.1:8000/v1/actions/ACTION_ID/approve \
  -H 'Content-Type: application/json' \
  -H 'X-Actor: lead@example.com' \
  -d '{"approver":"lead@example.com","reason":"Reviewed and authorized"}'

curl -s -X POST http://127.0.0.1:8000/v1/actions/ACTION_ID/execute \
  -H 'X-Actor: lead@example.com'
```

## Safety model

The agent layer can propose actions but cannot change approval policy. The policy engine is
deterministic code. The mock executor is the only included executor; setting an environment
variable alone cannot make the repository change production systems.

Before production, replace header-based development identity with SSO/JWT, use an append-only
audit service, connect a secret manager, and build a least-privilege provider adapter. See
[`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Recommended first pilot

Start with service-desk triage: ingest a ticket, enrich and route it, require approval before
writing back to the service desk, and measure routing accuracy, handling time, override rate,
and failed actions. Add one production connector only after the evaluation set passes.

## OpenAI integration

The repository defaults to deterministic analysis so it is runnable without an API key. To use
OpenAI-backed specialists, set `OPENAI_API_KEY` and `IT_AGENT_ANALYSIS_MODE=openai`. The
coordinator calls the selected specialist agents concurrently, and each response is parsed into
a strict schema. Per-agent operation allowlists and the deterministic approval policy remain
outside the model.

Use a representative evaluation set before enabling the OpenAI mode in production. The
Responses API supports structured outputs, function tools, MCP tools, and parallel tool calls.
