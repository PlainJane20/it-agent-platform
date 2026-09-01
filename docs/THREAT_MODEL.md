# Threat model

## Protected assets

- Administrator credentials and service tokens
- Employee identity and device data
- Production endpoints and identity providers
- Audit integrity and approval identity

## Primary threats and controls

| Threat | Control |
|---|---|
| Prompt injection requests privileged work | Model output is advisory; policy is deterministic |
| Unauthorized external changes | Approval gate plus connector-side authorization |
| Duplicate execution | Stable idempotency key for every proposed action |
| Secret leakage | Environment/secret manager only; payloads must not contain secrets |
| Approval spoofing | API requires actor identity; production must replace header auth with SSO/JWT |
| Missing accountability | Every workflow, decision, approval, and execution is audited |
| Excessive blast radius | Mock mode by default; scoped provider roles and per-action validation |

## Before production

Replace `X-Actor` development authentication with verified SSO/JWT claims, move audit records
to an append-only central store, encrypt sensitive fields, add retention policies, perform a
privacy review, and test every connector using a non-production tenant.

