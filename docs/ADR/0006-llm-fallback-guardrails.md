# ADR-0006: LLM Fallback Guardrails, Budget Capping & Data Isolation

## Status
Accepted

## Date
2026-11-04

## Context
Classifying unstructured ad copy into a two-level business category taxonomy and resolving ambiguous business names can benefit from Large Language Model (LLM) reasoning. However, unconstrained LLM invocations introduce severe cost inflation risks, prompt injection vulnerabilities from scraped web content, and potential data privacy leaks if contact data is forwarded to external AI APIs.

## Decision
1. **Rules First:** All category and entity classification must pass through deterministic rule-based keyword matching and regex filters first.
2. **LLM as Capped Fallback:** LLM inference (Gemini 1.5 Flash or Claude 3.5 Haiku) is deployed strictly as an optional fallback for items unresolved by deterministic rules.
3. **Data Sanitization & Isolation:** Under no circumstances should contact details (phones, emails, names) be sent to LLM endpoints. Only sanitized ad headline and body text are forwarded.
4. **Prompt Injection Mitigation:** Scraped text is interpolated into user content blocks with explicit instruction delimiters; LLMs have zero tool-calling privileges and zero access to system secrets; outputs must conform to a strict Pydantic JSON schema.
5. **Hard Budget & Cache:** LLM inference calls must check and debit `budgets.scope = 'llm'` (hard monthly cap, default $50.00). All prompt inputs and outputs are cached by SHA-256 text hash in Redis to eliminate redundant queries.

## Consequences
- **Positive:** Keeps AI operating costs strictly bounded; prevents prompt injection from executing malicious actions; prevents PII exposure to third-party AI APIs.
- **Negative:** Categorization accuracy on rare or obscure ad phrasing is dependent on the depth of rule lists when the monthly LLM budget cap is reached.
- **Compliance:** Satisfies DPDP data minimization and security requirements regarding third-party AI processors.

