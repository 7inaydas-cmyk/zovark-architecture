# ADR-0007: Webhook-only ingest

**Status:** accepted  
**Date:** 2026-04-28  
**Owner:** ingest-owner  
**Version context:** v3.2.5.0 consolidation promotion from zovark-v1-bootstrap-v3.2.3.2-final.zip  
**Source classification:** bootstrap predecessor ADR, mechanically normalized for current ADR format
## Context

SIEM platforms have heterogeneous integration mechanisms (push webhook, poll API, syslog, message queue). Supporting all of them creates an unbounded adapter surface. Concentrating on a single ingest pattern reduces complexity and aligns with how modern SIEM platforms expose their detection findings.

## Decision

Ingest is webhook-only. v1.0 endpoints are `/api/v1/ingest/splunk`, `/api/v1/ingest/elastic`, `/api/v1/ingest/sentinel`, `/api/v1/ingest/wazuh`, `/api/v1/ingest/generic`. Each endpoint is API-key-authenticated, idempotency-key-deduplicated, and rate-limited per tenant.

SIEM platforms that don't push webhooks natively (poll-only, syslog-only) are not supported in v1.0. A future ADR may add pull-mode if a customer commitment justifies it.

## Consequences

**Positive.** Single ingest pattern reduces complexity. Push-mode aligns with modern SIEM capabilities. Idempotency at the webhook is straightforward.

**Negative.** Customers using legacy SIEMs without webhook capability cannot integrate in v1.0. Pull-mode becomes a feature request gate.

## Alternatives Considered

N/A — original ADR did not address this.

## Fitness functions

- `tests/contract/ingest/idempotency.test.py` — for each ingest endpoint, asserts duplicate webhook delivery returns the cached result.
- `tests/architecture/ingest-pattern.test.py` — asserts no module under `src/adapters/inbound/` implements pull-mode or message-queue-mode ingest.

## References

- `zovark.md` §13.1
