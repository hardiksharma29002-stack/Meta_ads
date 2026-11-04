# ADR-0012: Modular Monolith Architecture with Asynchronous Task Queues

## Status
Accepted

## Date
2026-11-04

## Context
Engineering teams frequently default to microservices architectures prematurely, introducing network latency, distributed transaction complexities, deployment overhead, and complex inter-service messaging buses. For AdAtlas v1, all core functional requirements can be satisfied within a single unified repository and deployable unit.

## Decision
1. Adopt a **Modular Monolith** architecture implemented in Python 3.12+ with FastAPI.
2. Maintain strict internal directory boundaries (`collectors`, `pipeline`, `services`, `api`, `workers`) with enforced dependency constraints.
3. Decouple high-latency, I/O-intensive workloads (web crawling, contact extraction, metric rollups) into background worker processes orchestrated via Celery and Redis.
4. Split individual services into standalone microservices ONLY when an ADR proves an unresolvable scaling bottleneck.

## Consequences
- **Positive:** Drastically simplifies local development, deployment, transaction management, and end-to-end testing; enables zero-latency in-process function calls between domain services.
- **Negative:** Requires rigorous internal module discipline to prevent circular imports and architectural coupling.
- **Compliance:** Simplifies security audits and compliance controls by maintaining a single, auditable backend codebase.

