# Operations guide

This guide describes how to operate the reference implementation and what must change before a
production deployment.

## Runtime modes

| Analysis | Execution | Intended use |
|---|---|---|
| `deterministic` | `mock` | Local development, CI, and safe demonstrations |
| `openai` | `mock` | Model evaluation without external side effects |
| `openai` | custom connector | Production candidate only after all readiness controls pass |

The repository does not ship a live connector. `IT_AGENT_EXECUTION_MODE=live` does not create one.

## Health and startup

Run the service with:

```bash
uvicorn it_agent_platform.api:app --host 0.0.0.0 --port 8000
```

Use `GET /health` for a basic process health check. A production implementation should add
readiness checks for the audit store and configured provider dependencies.

## Data and backup

SQLite stores audit events at `IT_AGENT_DB_PATH`. For local development, back up the database
before replacing it. For production, use a centralized append-only store with encryption,
retention, access logging, and an independently administered deletion policy.

Pending actions currently reside in application memory and do not survive a restart. Durable
workflow state is required before production use.

## Observability baseline

Capture the following without logging request bodies or secrets:

- Workflow count, latency, completion state, and routed specialists
- Actions proposed, approved, rejected, failed, and executed
- Human override and policy-block rates
- Connector latency, retry count, provider request ID, and error category
- Model latency, token usage, schema failures, and allowlist rejections

Correlate telemetry by workflow ID and action ID.

## Incident procedures

If unsafe or unexpected behavior is observed:

1. Disable the production connector or revoke its credential.
2. Preserve audit and application logs.
3. Identify affected workflow and action IDs.
4. Confirm the provider-side outcome using its request ID.
5. Roll back through the provider's approved process when possible.
6. Add the scenario to the regression and evaluation suites.
7. Rotate credentials if exposure is suspected.

## Production readiness checklist

- [ ] Verified SSO/JWT identity replaces `X-Actor`
- [ ] Role-based permission checks cover approval and execution
- [ ] Provider credentials use a managed secret store
- [ ] Connector permissions are least privilege and tenant-scoped
- [ ] All connector operations have explicit allowlists
- [ ] Target validation is repeated immediately before execution
- [ ] Durable workflow and action state is implemented
- [ ] Audit storage is append-only, encrypted, monitored, and retained
- [ ] Sensitive data is classified, minimized, and redacted
- [ ] Idempotency, timeout, retry, and partial-failure behavior is tested
- [ ] Model evaluation and prompt-injection suites pass
- [ ] Rollback and credential-revocation procedures are rehearsed
- [ ] Privacy, security, and change-management reviews are complete

