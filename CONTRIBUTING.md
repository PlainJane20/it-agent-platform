# Contributing

Thank you for helping improve IT Agent Platform. Changes should preserve the project's central
security property: model output can propose work, but deterministic application code controls
authorization and execution.

## Development setup

```bash
git clone https://github.com/PlainJane20/it-agent-platform.git
cd it-agent-platform
make install
make check
```

Create a branch from `main` and keep each pull request focused on one outcome.

## Pull request expectations

- Explain the operational problem and the proposed solution.
- Add or update tests for behavioral changes.
- Update public documentation and the changelog when applicable.
- Keep secrets, production identifiers, and personal data out of fixtures and logs.
- Preserve mock execution as the default.
- Document new action kinds, connector operations, and approval implications.
- Run `make check` before requesting review.

## Adding a specialist

1. Implement the `SpecialistAgent` interface.
2. Give the specialist a narrow responsibility.
3. Add only the minimum allowed connector operations.
4. Return typed evidence and proposed actions.
5. Add routing, allowlist, policy, and prompt-injection tests.

## Adding a connector

A production connector must:

- Authenticate with a least-privilege service identity.
- Revalidate the actor, operation, and target at execution time.
- Reject operations outside an explicit allowlist.
- Use the supplied idempotency key.
- Return a provider request ID suitable for audit correlation.
- Avoid logging secrets or unnecessary personal data.
- Include contract tests against a non-production tenant.

## Commit style

Use concise, imperative commit subjects, for example:

```text
Add Jira sandbox ticket executor
Require approver role for privileged actions
Document audit retention controls
```

