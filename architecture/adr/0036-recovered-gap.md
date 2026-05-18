# ADR-0036 — Recovered Gap

## Status

GAP — source artifact not located during v3.2.3.5 baseline restoration.

## Context

ADR-0036 is referenced inline in this repo's downstream documentation and
in ZOVARK-v3.2.4.3-CLOSURE.md, but a full ADR body could not be located in
any artifact examined during the baseline restoration on 2026-05-18:

- zovark-v1-bootstrap-v3.2.3.2-final.zip (contains ADR-0001 through ADR-0035 only)
- /home/excelsior/Desktop/Archive/zvkfinal/architecture/adr/ (ADR-0001-0021)
- ZOVARK_v3.2.4.2_PATCH_REVIEW.md
- ZOVARK_BUILD_START_CONTRACT_v3.2.4.1.md
- ZOVARK-v3.2.4.3-CLOSURE.md (inline reference only, no body)
- CodArch and ZovArch extracted v3.2.4.5 and v3.2.4.6 patches

## Decision

The ADR number remains reserved. This file documents the gap explicitly.
No architectural commitment is made under this number until the original
source material is located or the ADR is re-authored under a separate PR.

## Consequences

- Cross-references to ADR-0036 in current documentation (ADR-0052,
  docs/positioning.md, docs/adr-status-table.md, etc.) are forward-references
  pending body recovery.
- Phase 2C bounded-retrieval implementation does not depend on ADR-0036.
- Re-authoring should not be combined with baseline-restoration PRs.

## Alternatives Considered

- Re-author from inline references: rejected for this PR — re-authoring
  is a substantive architectural act that belongs in its own ADR PR with
  its own Codex review.
- Skip the number entirely: rejected — removes a referenced identifier
  and breaks continuity with downstream cross-references.

## References

- Restoration tracking: PR on branch restore/legacy-baseline-recovery
  against main at 9ef42f2 on 2026-05-18.
