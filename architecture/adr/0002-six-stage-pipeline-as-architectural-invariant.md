# ADR-0002: Six-stage pipeline as architectural invariant

**Status:** accepted  
**Date:** 2026-04-28  
**Owner:** architect  
**Version context:** v3.2.5.0 consolidation promotion from zovark-v1-bootstrap-v3.2.3.2-final.zip  
**Source classification:** bootstrap predecessor ADR, mechanically normalized for current ADR format
## Context

The investigation pipeline must be predictable, composable, and replayable. A pipeline with implicit stages or undocumented control flow makes deterministic replay impossible and makes adding new analysis logic require codebase-wide changes.

## Decision

The pipeline is exactly six stages: `INGEST → ANALYZE → EXECUTE → ASSESS → GOVERN → STORE`. All six are Temporal activities orchestrated by `InvestigationWorkflow`. Stages communicate via Temporal workflow state, never via direct calls. Each stage is independently replayable; recording happens at stage boundaries.

The fast-path router can skip EXECUTE for fully-templated investigations. The archive path bypasses the pipeline entirely for trivial alerts. No other stage skipping is permitted.

## Consequences

**Positive.** Adding new analysis logic happens within a stage, not across the pipeline. Replay determinism is structural — the workflow event history captures exactly the six stages in order. Each stage has its own latency budget and its own metric set.

**Negative.** Six stages is a commitment. Future analysis patterns that don't fit the six-stage model require an ADR to add a stage; the cost of pipeline evolution is high.

## Alternatives Considered

N/A — original ADR did not address this.

## Fitness functions (planned, not yet built)

- `tests/architecture/pipeline-stages.test.py` — will assert that the pipeline implementation contains exactly six stages with the named order.
- `tests/architecture/pipeline-replayability.test.py` — will replay a synthetic workflow and assert byte-identical reconstruction of stage transitions.

## References

- INV-004 (deterministic verdict), INV-005 (replayable)
- `zovark.md` §4
