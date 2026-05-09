# Stale Docs Cleanup Plan

Status: cleanup plan, docs-only. This document does not archive, delete, banner, or
rewrite existing files.

## Execution State

This cleanup plan has not been executed. Several listed stale-doc paths are absent
from the current `zovark-architecture` repo, and no archive, banner-mark, delete,
or replacement action has occurred in this repo yet. The plan is preemptive and
future-facing for stale docs that may be imported, rediscovered, or migrated from
older repo lineage. Execution remains a separate future docs-only action.

## Purpose

The V3 ground-truth check found that some older product/runtime docs describe the V2
template/code-generation/sandbox pipeline as if it were the current architecture.
The current architecture direction is V3 forward, Slice proof absorbed. Stale docs
must be marked or archived so future work does not mistake legacy V2 descriptions
for the active default.

## Stale Or Potentially Stale V2 Docs

The following `Zovark_final` docs should be reviewed for stale banners or archive
treatment if they are imported, mirrored, or treated as governing docs:

| Path | Current Issue | Suggested Treatment |
| --- | --- | --- |
| `docs/ARCHITECTURE.md` | Describes V2-style template fast-fill, LLM parameter extraction, generated Python code, AST prefilter, and Docker sandbox as primary pipeline. | Banner-mark stale, then replace with V3-forward source-of-truth pointer. |
| `docs/pipeline_stages.md` | Describes older pipeline-stage behavior and may not reflect V3 tools default. | Banner-mark stale or archive after extracting any still-valid implementation details. |
| `docs/pipeline_map.md` | Maps older V2 pipeline paths and may conflict with V3 active/default path. | Banner-mark stale or archive. |
| `docs/ZOVARK_IMPLEMENTATION_AUDIT.md` | Historical audit context, not current source-of-truth. | Keep as historical if needed, but banner as non-governing. |
| any v2/v3 transition notes not tied to current refs | May contain benchmark or architecture claims that are branch-specific. | Banner with branch/ref scope and do not treat as governing. |

This plan does not modify the older repo. It records cleanup work required if those
docs are brought into the current architecture process.

## Docs To Preserve As Evidence

These current repo docs should remain as evidence docs, not necessarily as final
governing specs:

- `docs/v3-ground-truth-check.md`
- `docs/adr-index-and-architecture-constraints.md`
- `docs/v3-asset-inventory.md`
- `docs/v3-to-v4-domain-map.md`
- `docs/v3-fixture-capture-report.md`
- `docs/architecture-reconciliation-v4-1-to-slice-001.md`
- `docs/post-slice-001-roadmap.md`

They explain how the current synthesis was reached. They should not be deleted just
because a final architecture synthesis exists.

## Final Source-Of-Truth Set After Freeze

After review of PR #29 and any follow-up cleanup, the intended source-of-truth set is:

1. `architecture/source-of-truth.md`
2. `architecture/adr-index.md`
3. active ADRs and architecture-governing decision records
4. `docs/final-architecture-v3-v4-replay.md`
5. `docs/capability-identity-contract.md`
6. `docs/implementation-sequence.md`
7. `docs/stale-docs-cleanup-plan.md`
8. relevant OpenSpec specs

Evidence docs remain useful, but the final synthesis and active ADRs should govern
future implementation decisions unless contradicted by a new ADR or validated customer
signal.

## Proposed Banner Text

Use a short banner like this when stale docs are banner-marked in a future PR:

```text
Status: historical/stale.

This document describes an older V2 or transition-state architecture. The current
architecture source of truth is the V3-forward, Slice-proof-absorbed synthesis in
docs/final-architecture-v3-v4-replay.md plus active ADRs. Do not use this document
as a governing source without checking current architecture docs.
```

## Cleanup Phases

### Phase 1: Identify

Status: this plan.

- List stale V2 docs.
- Identify evidence docs that should remain available.
- Define final source-of-truth set.

### Phase 2: Banner

Future docs-only PR.

- Add stale banners to imported or mirrored V2 docs.
- Add cross-links to the current synthesis and ADR index.
- Do not change runtime behavior.

### Phase 3: Archive

Future docs-only PR if needed.

- Move stale docs to an archive location only after links and references are updated.
- Preserve commit/ref evidence used by PR #25 through PR #29.
- Do not remove evidence required for claim provenance or ADR cross-links.

### Phase 4: Freeze Review

Future architecture review.

- Confirm source-of-truth hierarchy.
- Confirm no stale doc remains linked as active architecture.
- Confirm the architecture freeze trigger has not been hit.

## Freeze Trigger

This cleanup plan follows the architecture freeze trigger from the final synthesis.
The architecture should remain stable until the earliest of:

- first paying customer
- first failed pilot
- six months from the freeze date
- first significant customer signal contradicting current decisions

If a trigger occurs, update active ADRs or architecture-governing decision records
before changing source-of-truth documents.

## Non-Goals

This plan does not:

- delete files
- archive files
- update `Zovark_final`
- change proof-package schema
- add a V3 adapter
- define Investigation Trace V1
- implement manifest/provenance/signing
- start live EDR/SIEM connector work
- create legal, certification, or forensic-completeness claims
