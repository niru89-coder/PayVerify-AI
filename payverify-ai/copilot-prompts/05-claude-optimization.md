# Phase 3.5 — Claude API Optimization (AI Gateway)

**Goal:** Minimize cost, latency, and data exposure for Claude-based variance explanations.

This is the most important phase from a security and cost standpoint.

## Hard constraint — data minimization

Claude must **never** receive:

- Payroll registers (client or platform)
- Excel files
- PDFs
- Employee master data
- Rule source documents

Claude should receive **only** the already-classified variance payload:

```json
{
  "rule_id": "...",
  "component": "...",
  "expected_value": 0.0,
  "actual_value": 0.0,
  "variance_type": "...",
  "metadata": { }
}
```

## Tasks

Build an **AI Gateway service** (e.g. `services/ai_gateway.py`, sitting between
`agents/explanation_agent.py` and the Anthropic API) that:

1. Reduces prompt size — strips the payload down to only the fields listed above before it
   ever reaches the Claude client.
2. Removes unnecessary fields (defense in depth — even if a caller accidentally passes extra
   PII/register data, the gateway filters it out via an explicit allow-list, not a deny-list).
3. Caches duplicate requests (e.g. keyed by a hash of `rule_id + component + variance_type +
   rounded values`, backed by the Redis instance from Phase 3.1/3.4) to avoid redundant API calls
   for identical variances.
4. Logs every prompt sent (and response received) for audit purposes — logs must NOT contain
   any of the disallowed fields, only the minimized payload.
5. Tracks token usage per request and cumulatively (expose via the `/metrics` endpoint from
   Phase 3.6).
6. Provides fallback responses if the Claude API is unavailable or errors — reuse the existing
   `StubExplanationProvider` deterministic template as the fallback, so the user always gets an
   explanation.

## Hard constraint — deterministic validation independence

The deterministic rule engine and reconciliation/classification pipeline must always complete
successfully even if Claude is completely offline. AI explanation is an optional enrichment step
called only on-demand (`POST /variances/{id}/explain`), never a dependency of the validation run
itself. Verify this remains true after the gateway is introduced.

## Deliverable

- `services/ai_gateway.py` — gateway implementing minimization, caching, logging, token tracking,
  and fallback
- Updated `agents/explanation_agent.py` to route through the gateway
- Unit tests proving: (a) disallowed fields are never forwarded to the Claude client, (b) cache
  hits skip the API call, (c) fallback triggers correctly when the API errors/times out

## Acceptance Criteria

- A test that constructs a variance payload containing extra register/PII-like fields confirms
  none of those fields appear in the actual outbound Claude request.
- Requesting an explanation for the same variance twice results in only one real API call.
- Simulated API failure still returns a usable explanation to the user.
