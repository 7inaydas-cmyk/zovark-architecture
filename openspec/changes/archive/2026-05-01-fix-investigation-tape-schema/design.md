## Context

The `product-wedge` spec at `openspec/specs/product-wedge/spec.md` requires that "the **investigation tape** is named as the central recorded object" in every architecture overview. The `mvp-scope.md` patch-tree document lists the tape's contents informally ("recorded investigation object containing raw evidence references, model/tool I/O records when used, timeline, findings, verdict/conclusion, and policy snapshot"). No document defines the tape as a structured object: required vs. optional fields, lifecycle states, or how the tape composes with EDR handoff, replay, and audit chain.

The bootstrap package (v3.2.4.6) does not implement runtime tape, replay, or audit chain — so this change is documentation only. The aim is a spec good enough for build planning: an engineer reading it should be able to scope the tape's storage, the tape API, and the tape UI without further ambiguity, and should be able to identify which fields are MVP-required vs. post-MVP additions.

## Goals / Non-Goals

**Goals:**

- Enumerate the tape's required fields with conceptual types (string, ISO-8601 timestamp, list of evidence references, etc.).
- Define lifecycle states (e.g., `recording` → `closed` → `replaying`) and the transitions between them.
- Identify the customer-facing surface — the subset of the tape a design-partner reviewer can inspect.
- Define the tape's relationship to EDR handoff record, replay state, audit chain entry, and rollback plan (without defining those objects in full — separate changes do).
- Mark MVP-required fields vs. post-MVP additions explicitly.

**Non-Goals:**

- JSON Schema, Avro, Protobuf, or any wire format.
- Storage decisions (object store vs. database vs. blob; encryption; replication).
- Tenant-scoping implementation (scoping is an invariant; how to implement it is M1+).
- UI/UX of the tape review screen.
- Defining the EDR handoff record, replay state, or audit chain entry — those are separate rc2 changes.
- Implementing any code.

## Decisions

### Field categorization

Fields are grouped into 8 categories:

1. **Identity** — tape ID, tenant ID, creation timestamp, schema version, source-alert reference.
2. **Raw evidence** — list of evidence references (each with hash, source type, ingestion timestamp, optional retention class).
3. **Recorded model/tool I/O** — list of records, each with model identity, model version, tool identity, tool version, prompt hash, response hash, decision contribution. Required when models/tools were used; absent when fully deterministic.
4. **Timeline** — ordered list of events with type, timestamp, actor, evidence references, decision-contribution flag.
5. **Findings** — list of evidence-backed findings, each with title, severity, evidence references, model contribution flag, confidence band.
6. **Verdict** — final verdict (deterministic enum), evidence references, model contribution flag, signing/auth tag.
7. **Handoff** — reference to EDR handoff record (separate object spec) plus inline summary fields (action type, target, approval mode, execution status). Optional — present only when a handoff occurred.
8. **Audit and replay** — references to audit chain entries (separate spec), replay state (separate spec), and rollback plan (referenced from handoff).

**Rationale.** Categorization gives reviewers a stable mental model and lets future spec changes target a category without rippling. Alternative considered: flat field list. Rejected — the tape has too many fields for a flat list to stay legible.

### Lifecycle states

Three states: `recording`, `closed`, `replaying`. Transitions:

- `recording` → `closed`: tape is sealed (audit root signed, no further field appends).
- `closed` → `replaying`: tape is being replayed (read-only, replay state object tracks current position).
- `replaying` → `closed`: replay finished.

**Rationale.** Closed is the canonical archive state; replays don't mutate the tape, only the replay state object. Alternative considered: more states (e.g., `partial`, `corrupt`, `legal-hold`). Rejected for now — those are post-MVP. Track as a `MODIFIED Requirements` follow-up if needed.

### MVP-required vs. post-MVP fields

MVP-required (must exist on every tape):
- All Identity fields.
- All Raw evidence references with hashes.
- Timeline (may be empty for trivial cases but field present).
- At least one Finding OR a no-findings flag.
- Verdict (with deterministic enum from a small fixed set).
- Audit chain reference (even if a placeholder during MVP).

Post-MVP optional:
- Recorded model/tool I/O — required only if models/tools were used.
- Handoff reference — required only if a handoff occurred.
- Replay state — present only when replaying.
- Confidence bands on findings — recommended but not required.

**Rationale.** MVP is design-partner review. Reviewers must always see evidence and verdict; the model/tool I/O is "nice to have" for the first wave but adds review depth. Alternative considered: require model I/O always. Rejected — many MVP investigations are deterministic-rule-driven and have no model I/O.

### Customer-facing surface

A reviewer accessing a tape can see:

- Tape ID, tenant ID, source-alert reference.
- Raw evidence list (hashes + retrievable links via tenant-scoped vault, when M1+ vault is online).
- Timeline (full).
- Findings with severity and evidence links.
- Verdict (full).
- Handoff record summary (action, target, approval mode, execution status, rollback plan summary).
- Replay availability (yes/no).

Reviewers do **not** see:

- Internal authorization records (those are in vault audit, not the tape).
- Raw model prompts/responses unless explicitly opted in (raw I/O can be sensitive).
- Cross-tenant data of any kind.

**Rationale.** Match the wedge — the tape IS the product surface for design-partner trust. The exclusions are operational/security necessities. Alternative considered: full transparency including model I/O. Rejected — model I/O may carry tenant-confidential prompts.

## Risks / Trade-offs

- **Risk:** the spec is too coarse to be useful for build planning. → **Mitigation:** the field list names types (string, list, enum) and required-ness; that is the right level for spec, with implementation choosing serialization.
- **Risk:** confidence bands and similar M-N-only fields cause future schema churn. → **Mitigation:** marked post-MVP optional; a `MODIFIED Requirements` change is needed to make any post-MVP field MVP-required.
- **Trade-off:** referencing other objects (EDR handoff, replay state) before they're specified creates forward-references. Accepted: those specs land in subsequent rc2 changes; cross-spec references are normal.

## Migration Plan

1. Land `architecture/objects/investigation-tape.md` with the categorized field list, lifecycle, MVP/post-MVP classification, and customer-facing surface.
2. Capture the spec via `openspec archive`.
3. The subsequent `fix-edr-handoff-schema` and `fix-replay-and-audit-semantics` changes reference this object's fields by name.

**Rollback:** revert. The tape goes back to being signposted by the wedge but undefined.

## Open Questions

- Should retention-class on raw evidence be MVP-required (drives RPO/RTO conversations)? Defer — currently optional; revisit when DR sketch lands per ARCH-P2-002.
- Should the verdict enum live in this spec or in a separate `verdicts` capability? Defer — for now, verdicts are a small fixed set defined inline. If the set grows, split into its own spec.
