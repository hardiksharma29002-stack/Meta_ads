# ADR-0005: Authentication Strategy via Google OAuth, Auth.js & Signed BFF JWTs

## Status
Accepted

## Date
2026-11-04

## Context
AdAtlas is an internal marketing intelligence platform. Managing custom username/password registries creates credential stuffing vulnerabilities and unnecessary maintenance. Furthermore, direct exposure of the FastAPI REST backend to browser sessions complicates CSRF mitigation and token revocation.

## Decision
1. Standardize authentication on Google OAuth 2.0 restricted strictly to company-owned email domains (`@company.com`).
2. Utilize Auth.js (NextAuth) within the Next.js BFF (Backend-for-Frontend) layer to manage secure, HTTP-only, encrypted session cookies.
3. For server-to-server calls from the Next.js BFF to the FastAPI backend, the BFF signs a short-lived (5-minute expiry) JWT bearer token using HMAC-SHA256 containing user ID, email, and verified role claims.
4. FastAPI validates the incoming JWT signature, enforces Role-Based Access Control (`viewer`, `marketing`, `compliance`, `admin`), and attaches the user context to the request state.

## Consequences
- **Positive:** Eliminates password storage liability; enforces centralized company SSO; isolates backend API inside private network namespace.
- **Negative:** Requires active Google Workspace OAuth client credentials; offline development requires a mock JWT signing provider.
- **Compliance:** Enforces enterprise identity governance and provides non-repudiable user identifiers for `audit_log`.

