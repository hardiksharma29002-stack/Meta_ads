# ADR-0003: Meta Graph API Identity Confirmation & Credential Isolation

## Status
Accepted

## Date
2026-11-04

## Context
Accessing Meta's Ad Library API (Adapter A) requires a registered Meta Developer account, identity confirmation with government-issued photo identification, and developer app authorization. Autonomous engineering agents cannot complete physical identity verification or sign developer legal agreements on behalf of the organization.

## Decision
1. The human system owner is responsible for registering the Meta Developer App, completing national identity verification, and generating the necessary App ID, App Secret, and long-lived User Access Token.
2. The engineering codebase and autonomous agents will utilize `.env.example` placeholder configurations and mock recorded test fixtures (`vcrpy`/`respx`) during development and CI testing.
3. Production API tokens are managed via secure environment variables injected at deployment time and are never checked into version control.

## Consequences
- **Positive:** Ensures clear human accountability for Meta developer terms; eliminates secrets from code repositories.
- **Negative:** Adapter A integration testing in development relies entirely on recorded cassettes until the human owner supplies verified credentials.
- **Compliance:** Prevents unauthorized identity delegation and complies with Meta developer policies.

