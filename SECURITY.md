# Security policy

## Reporting a vulnerability

Please do not disclose suspected vulnerabilities in a public issue. Use GitHub's private
vulnerability reporting feature for this repository, or contact the repository owner privately
through the profile information associated with [@PlainJane20](https://github.com/PlainJane20).

Include:

- The affected component and version or commit
- Reproduction steps or a minimal proof of concept
- The potential impact
- Any suggested mitigation

Do not include real credentials, employee data, or production system identifiers.

## Security scope

Security-sensitive areas include authorization boundaries, action approval, connector allowlists,
identity propagation, audit integrity, prompt injection resistance, secret handling, and duplicate
execution prevention.

## Supported versions

Until the first stable release, security fixes are applied to the latest commit on `main`.

## Deployment notice

The included `X-Actor` header is a development mechanism, not authentication. The included mock
executor performs no external side effects. Deployers are responsible for adding verified SSO/JWT
identity, role-based authorization, encrypted storage, and least-privilege provider credentials.

