## Context

rc3 freeze gives 8 governing specs + 5 architecture object docs + scorecard + decision log. The corpus is detailed enough to drive build, but no single page summarizes it. Builders are most productive with a wedge-to-output mental model that fits on one screen. This change creates that artifact and codifies the rules so future updates don't sprawl.

## Goals / Non-Goals

**Goals:**

- The one-pager fits on one printed page (target: ≤ 100 lines of markdown).
- It uses the canonical wedge statement and core flow verbatim.
- Core object descriptions reference the canonical field names from `openspec/specs/` rather than inventing colloquial ones.
- Deferred scope is explicit and matches the rc3 scorecard's `PASS-with-explicit-DEFERRAL` annotations (M2 DR sketch, M3 vault IPC, post-apply cross-link verification).
- The first MVP build slice is the smallest path that exercises every governing spec.
- A Mermaid diagram (`.mmd`) renders the same flow.

**Non-Goals:**

- New ADRs.
- Modifying any existing OpenSpec spec.
- Adding product capabilities, vendor support, or autonomous-action scope.
- Documentation depth equal to the spec set (the specs are the source of truth; this is a map).
- A separate "architecture overview" document beyond the one-pager.

## Decisions

### Use canonical field names, not colloquial ones

The user's template uses friendly labels (e.g., "raw evidence ledger" for what the spec calls `raw_evidence`; "EDR handoff recommendation" for what the spec calls the `edr-handoff` record). The one-pager uses both: a friendly section title and the canonical field name in parentheses, e.g., `### Investigation Tape (\`investigation-tape\` capability)`. Sub-fields list canonical names (`tape_id`, `tenant_id`, `raw_evidence`, etc.).

**Rationale.** Friendly labels survive without context; canonical names anchor every reader to the actual spec. Both serve different audiences without inventing a third vocabulary. Alternative considered: only colloquial. Rejected — drifts from the source.

### MVP slice = the seven-step path

Per rc3 scorecard's "Bridge to product implementation": 1 EDR sample → 1 tape → 1 timeline → 1 evidence ledger → 1 verdict → 1 EDR handoff recommendation → 1 replay report. The one-pager preserves this exactly as the runtime path of the first slice.

**Rationale.** The slice is already declared; copying it preserves consistency and proves the one-pager is derived, not invented.

### Deferred section pulls from rc3 scorecard

The scorecard's `PASS-with-explicit-DEFERRAL` annotations name owner + milestone + acceptance for two categories: #8 (DR sketch, M2, architect) and #9 (M3 IPC schemas, M3, schema-owner). The "Tracked deliverables for post-rc3" table lists ten items. The one-pager picks the most architecturally significant ones (live EDR, vault runtime, autonomous action, multi-tenancy, Sigma, DR drills, customer dashboards) — these are the "what's NOT in the first slice" set. The owner+milestone level of detail stays in the scorecard; the one-pager just lists.

**Rationale.** The one-pager is a map, not a deliverable tracker. Linking ("see the rc3 scorecard for owner + milestone") is sufficient.

### Mermaid diagram structure

Two subgraphs: `MVP Slice` (the seven steps + replay report) and `Deferred` (the off-slice scope). Edges within MVP show the data flow; the Deferred subgraph has no edges to MVP — it's a list, not a path. This visual asymmetry signals that deferred items are explicitly out of the first build.

**Rationale.** Mermaid does not have native "out of scope" semantics; the no-edge subgraph is the cleanest visual indicator. Alternative considered: dashed edges from MVP to Deferred showing "could connect in future." Rejected — implies a roadmap commitment the one-pager isn't qualified to make.

### One-pager must NOT modify the rc3 scorecard

The user's prompt explicitly says: "After creating the files, update architecture/review/release-candidate-scorecard.md only if it has a section for build-readiness notes. Otherwise do not modify it." The rc3 scorecard already has a "Bridge to product implementation" section; the one-pager refers to it but doesn't edit it.

**Rationale.** rc3 is tagged. Mutating tagged-version content from a docs branch would diverge it from the tag. Refer-don't-edit is the disciplined move.

### Capability `build-planning-artifacts`

The capability's requirements:

- The one-pager exists at `architecture/one-page-architecture.md`.
- It contains the canonical wedge statement and core flow verbatim.
- It declares the first MVP build slice.
- It lists deferred scope.
- It accompanies a Mermaid diagram at `architecture/one-page-architecture.mmd`.
- It does NOT introduce new architecture decisions.
- Updates go through `MODIFIED Requirements` against this capability.

**Rationale.** The one-pager is small, but small things drift. Codifying the rules now means future "let's just add one more thing" pressure has to go through a spec change. Alternative considered: skip the spec, just commit the doc. Rejected — every prior architecture artifact has a governing spec; this should too.

## Risks / Trade-offs

- **Risk:** the one-pager drifts from the underlying specs as those specs evolve. → **Mitigation:** the spec requires that the one-pager preserve the canonical wedge and reference current capabilities. Future spec changes that touch wedge/objects MUST also update the one-pager (enforced at review time).
- **Risk:** the page-fit constraint forces oversimplification. → **Mitigation:** the one-pager points at the underlying specs by name; readers who need depth follow the link.
- **Trade-off:** Mermaid diagram is one more thing to keep in sync. Accepted: the .mmd is small (~30 lines), and code review of changes is straightforward.

## Migration Plan

1. Add `architecture/one-page-architecture.md` and `architecture/one-page-architecture.mmd`.
2. Capture as `openspec/specs/build-planning-artifacts/spec.md` via archive.
3. Commit on `docs/one-page-architecture` branch; push.
4. Merge to `main`; push main.
5. Subsequent build planning starts from `main` post-merge; the user's intended next branch `mvp/slice-001-investigation-tape` is created from main.

**Rollback:** revert. The one-pager goes away; the specs remain as the only path to understanding.

## Open Questions

(none — scope is intentionally narrow)
