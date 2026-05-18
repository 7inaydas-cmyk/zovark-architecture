# ADR-0037 — Recovered Gap

## Status

GAP — source artifact not located during v3.2.3.5 baseline restoration.

## Context

ADR-0037 is referenced in downstream architecture documentation but a
full body could not be located in any artifact examined during the
baseline restoration probe on 2026-05-18:

- zovark-v1-bootstrap-v3.2.3.2-final.zip (contains ADR-0001 through ADR-0035 only)
- /home/excelsior/Desktop/Archive/zvkfinal/architecture/adr/ (ADR-0001-0021)
- ZOVARK_v3.2.4.2_PATCH_REVIEW.md (no ADR-0037 hit)
- ZOVARK_BUILD_START_CONTRACT_v3.2.4.1.md (no ADR-0037 hit)
- ZOVARK-v3.2.4.3-CLOSURE.md (no ADR-0037 reference, inline or otherwise)
- CodArch and ZovArch extracted v3.2.4.5 and v3.2.4.6 patches

Unlike ADR-0036, ADR-0037 does not even appear as an inline reference in
the v3.2.4.3 closure document. Its place in the architecture history is
inferred from continuity expectations, not from documentary evidence.

## Decision

The ADR number remains reserved. This file documents the gap explicitly.
No architectural commitment is made under this number until the original
source material is located or the ADR is re-authored under a separate PR.

## Consequences

- Any downstream documentation that references ADR-0037 should be
  treated as a forward-reference pending body recovery or supersession.
- Phase 2C bounded-retrieval implementation does not depend on ADR-0037.
- Re-authoring should not be combined with baseline-restoration PRs.

## Alternatives Considered

- Re-author from continuity inference: rejected — re-authoring without
  source material is substantive architectural work that belongs in its
  own ADR with its own Codex review, not in a baseline-restoration PR.
- Skip the number entirely: rejected — removing the number could break
  continuity assumptions in tooling that scans for sequential ADR
  identifiers.

## References

- Restoration tracking: PR on branch restore/legacy-baseline-recovery
  against main at 9ef42f2 on 2026-05-18.
