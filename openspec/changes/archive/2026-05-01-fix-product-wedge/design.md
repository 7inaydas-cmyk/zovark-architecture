## Context

Governance docs (`architecture/source-of-truth.md`, `architecture/review/finalization-checklist.md`) declare Zovark as "the tape recorder for cybersecurity investigations" with a canonical EDR-bookended core flow. Architecture content under `zovark-v3.2.4.6-engineering-ready/zovark-v3.2.4.6-patch/` does not echo this framing: the MVP product wedge in `mvp-scope.md` reads "Zovark records tenant-scoped security investigations, preserves evidence, reconstructs timelines, produces evidence-backed findings, derives deterministic verdicts when the verdict subsystem exists, and supports policy-gated external-action handoff." The mismatch trips finalization checklist criterion #1 (Product wedge clarity) and is filed as ARCH-P0-001 / GitHub #1.

The patch tree is a v3.2.4.6 bootstrap package that does not implement runtime tape, replay, audit chain, EDR adapter, or update factory. This change is therefore documentation-only: it reframes existing architecture and customer-facing prose without introducing new product capability or runtime behavior.

## Goals / Non-Goals

**Goals:**

- Establish a single canonical product-wedge statement and core-flow phrasing usable as a copy-paste verbatim block in any document.
- Apply that statement to the four documents that currently disagree: `architecture/source-of-truth.md` (already governance, light reinforcement), `mvp-scope.md`, `ZOVARK-v3.2.4.6-FINAL.md`, `ENGINEERING-READY-HANDOFF.md`.
- Subordinate generic "AI SOC platform" framing where it would otherwise dilute the wedge.
- Make investigation tape and EDR handoff visible as central concepts in architecture overviews.
- Land the change with no functional/architecture/spec impact other than positioning text.

**Non-Goals:**

- Defining the investigation tape object schema. (Future change; tracked via finalization checklist criterion #5.)
- Adding new product capabilities, EDR vendors, autonomous-action modes, or post-MVP claims.
- Touching ADRs, invariants, telemetry schemas, or scripts.
- Resolving ARCH-P1-001 (claim-provenance), ARCH-P1-002 (ADR-0043 pivot), ARCH-P2-001/002 (ADR drill / DR), or ARCH-P3-001 (corpora). These are tracked separately.
- Introducing implementation work or runtime behavior of any kind.

## Decisions

### Canonical product-wedge block

The block below is reproduced verbatim in every top-level architecture and customer-facing document:

> **Zovark is the tape recorder for cybersecurity investigations.**
>
> Core flow: **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

**Rationale.** Verbatim reuse eliminates drift. Documents may add elaboration immediately after the block, but the two-sentence wedge statement and the arrow-sequenced core flow MUST appear unchanged. Alternative considered: per-document paraphrase. Rejected because paraphrase is exactly what produced the current ARCH-P0-001 mismatch.

### Where the wedge block appears

- `architecture/source-of-truth.md` — under `## Current product wedge` (already in place; verify wording matches).
- `architecture/mvp-scope.md` (in patch tree) — replace the existing first paragraph of `## Product Wedge` with the canonical block, then keep the existing first-user / design-partner sentence as immediate elaboration.
- `ZOVARK-v3.2.4.6-FINAL.md` — append a `## Product wedge` section near the top (after the Summary) containing the canonical block.
- `ENGINEERING-READY-HANDOFF.md` — append a `## Product wedge` section after `## Purpose` containing the canonical block.

**Rationale.** Each document already has a natural location near the top for product framing; this minimizes structural disruption. Alternative considered: replace entire summary/intro sections. Rejected as too destructive — those sections also carry MVP-scope, package status, and engineering-handoff content that must survive intact.

### How investigation tape and EDR handoff are surfaced

In each document where the wedge block is added, follow it with one paragraph (1–3 sentences) clarifying:

- The **investigation tape** is the central recorded object — raw evidence, timeline, findings, verdict, EDR handoff record, rollback plan, replay state, audit references. (Conceptual reference only; the schema is future work.)
- The **EDR handoff** is replayable, evidence-linked, and reversible. (Conceptual reference only; the object spec is future work.)

**Rationale.** Promoting the two terms in every overview without redefining them keeps this change scoped to positioning while signposting the future work. Alternative considered: defer all mentions of tape/handoff until a follow-up change. Rejected because the wedge statement itself names them — leaving them undefined in adjacent prose would produce a worse experience than a one-paragraph signpost.

### Subordinating "AI SOC platform" framing

A repo-wide grep does not currently find "AI SOC platform" in the patch tree, so no immediate edit is required. The proposal lists it as a guard against future drift; this change records the rule as part of `specs/product-wedge/spec.md` so future edits to architecture content are checked against it.

**Rationale.** Establishing the rule once means subsequent contributors and AI agents have an explicit norm to violate or comply with, rather than rediscovering ARCH-P0-001 again.

## Risks / Trade-offs

- **Risk:** customer-facing language elsewhere in the patch tree (e.g., README, license preface) may diverge from the canonical block. → **Mitigation:** scope is intentionally narrow to the four named documents; future inventory passes will surface additional documents and we file them as new ARCH-* issues rather than letting this change sprawl.
- **Risk:** patch-tree documents are dated artifacts (v3.2.4.6 bootstrap) and may be replaced wholesale before MVP. Editing them now could be partly throwaway. → **Mitigation:** the wedge block is short and reusable; the cost of updating four sections is low. The architecture-finalization process treats those documents as authoritative until superseded.
- **Trade-off:** verbatim reuse is rigid — a future wedge revision requires touching every document. Accepted: drift is the worse failure mode. The block is short enough that mass-edit via `sed` or grep+rewrite is a one-shot operation.

## Migration Plan

1. Apply the wedge edits to the four documents (see `tasks.md`).
2. Verify every modified document contains the canonical block verbatim (`grep -F "Zovark is the tape recorder for cybersecurity investigations."`).
3. Verify every modified document contains the core-flow arrow sequence (`grep -F "EDR alerts → investigation tape → replayable evidence"`).
4. Update ARCH-P0-001 ledger entry to `status: fixed`, `fixed_by_openspec_change: fix-product-wedge`. Close GitHub #1 with a reference to the change.
5. Re-run finalization checklist criterion #1 to confirm pass.

**Rollback:** the change is documentation-only; revert the commits that touch `architecture/` and the patch-tree files if the wedge framing is later abandoned.

## Open Questions

- Should the canonical block also appear in the `OWNERS.yaml` repository-level description? Currently `OWNERS.yaml` describes individual components (F-002 tape recorder, F-004 EDR adapter) but not the product. Decision deferred — `OWNERS.yaml` is component-scoped, not product-scoped, and adding a product wedge there blurs that boundary. Track as a possible follow-up if owners-of-record context becomes a customer-facing surface.
