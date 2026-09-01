# Threat model

## Scope and assumptions

This threat model covers request ingestion, specialist analysis, action policy, approval,
execution, and audit recording. It assumes the host, dependency supply chain, identity provider,
and any future IT provider tenant may fail or be attacked and therefore require layered controls.

The current repository is a reference implementation. Its header-based actor identity and
in-memory action state are explicitly outside the production trust model.

## Protected assets

- Administrator credentials, service tokens, and provider sessions
- Employee identity, access, incident, and device information
- Production endpoints, identity providers, and service-management records
- Approval authority and action lifecycle integrity
- Audit evidence and correlation identifiers
- Model configuration, prompts, and operation allowlists

## Trust boundaries

1. **Client to API:** all request fields and headers are untrusted.
2. **API to model:** request content can contain prompt injection or sensitive information.
3. **Model to application:** structured output remains untrusted until schema and allowlist checks.
4. **Application to connector:** approved intent must be reauthorized and target-validated.
5. **Connector to provider:** credentials and provider responses cross an external boundary.
6. **Application to audit store:** evidence requires integrity, access control, and retention.

## Threats and controls

| Threat | Primary control | Verification |
|---|---|---|
| Prompt injection asks an agent to bypass policy | Model output is advisory; policy is deterministic | Injection regression tests |
| Model invents a powerful operation | Per-agent application allowlist | Allowlist unit tests |
| Model mislabels action risk or kind | Policy checks action type; connector reauthorizes operation | Adversarial evaluation set |
| Unauthorized approval | Verified SSO/JWT plus approver RBAC in production | Authorization integration tests |
| Approval is changed after review | Immutable action version or content hash before execution | Mutation and race tests |
| Duplicate execution | Stable idempotency key plus provider-side deduplication | Replay and retry tests |
| Target changes between approval and execution | Revalidate target immediately before provider call | Time-of-check/time-of-use tests |
| Secret leakage through prompts or logs | Secret manager, data minimization, and redaction | Secret scanning and log review |
| Sensitive data retained unnecessarily | Field classification, minimization, encryption, and retention policy | Privacy review |
| Audit events are altered or removed | Append-only centralized storage and restricted administration | Integrity and access audit |
| Connector credential has excessive scope | Dedicated least-privilege service identity | Provider permission review |
| Partial provider failure creates inconsistent state | Normalized receipts, reconciliation, and compensating procedure | Fault-injection tests |
| Dependency or CI compromise | Pinned workflow majors, Dependabot, review, and artifact validation | Supply-chain review |
| Denial of service or runaway cost | Authentication, rate limits, quotas, timeouts, and model budgets | Load and quota tests |

## Known limitations

- `X-Actor` can be spoofed and is suitable only for local development.
- Pending actions do not survive a process restart.
- SQLite audit records are mutable by a host administrator.
- The mock executor does not validate a real provider's authorization model.
- No rate limiting, tenant isolation, field-level encryption, or centralized telemetry is included.
- A representative model evaluation and prompt-injection corpus is not yet included.

## Production security gates

Do not enable a live connector until all of the following are true:

- Verified SSO/JWT and role-based approval authorization are enforced.
- Actions are durable, versioned, and immutable between approval and execution.
- Audit storage is append-only, encrypted, monitored, and retained.
- Provider credentials are managed, rotated, least privilege, and tenant-scoped.
- Provider operations have target validation, idempotency, and bounded failure handling.
- Sensitive fields have documented classification, minimization, and redaction behavior.
- Security, privacy, change-management, and recovery reviews are complete.
- Connector contract, adversarial model, replay, and fault-injection tests pass.

