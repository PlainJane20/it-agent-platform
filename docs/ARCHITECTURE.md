# Architecture

```text
Request
  -> deterministic coordinator routing
  -> parallel specialist analysis
  -> deterministic approval policy
  -> human approval for side effects
  -> connector execution
  -> append-only audit trail
```

## Trust boundaries

The coordinator and specialists propose actions; they do not bypass the policy engine. The
policy engine is deterministic application code. External writes, privileged changes,
destructive actions, and high-risk operations require human approval. The default connector
is a mock executor and produces no external side effects.

Specialists can run in deterministic mode or as parallel OpenAI Responses API calls with strict
structured outputs. Each specialist has an operation allowlist enforced after model output is
parsed. The model cannot add a new executable connector operation.

## Specialists

| Agent | Responsibility |
|---|---|
| Triage | Classification, priority, enrichment, and queue recommendation |
| Identity | Access, onboarding, offboarding, and account lifecycle |
| Incident | Incident timeline, evidence, containment, and recovery proposals |
| Endpoint | Device compliance, patching, and remediation proposals |
| Knowledge | Draft runbook and knowledge-base updates |
| Compliance | Evidence checklist and control implications |

## Production connector contract

Implement `ActionExecutor.execute`. A connector must enforce its own authorization, validate
the target, use the action's idempotency key, return a provider request ID, and avoid logging
secrets. Keep credentials in a managed secret store, never in request metadata or the audit DB.
