# MVP Scope

## Product Wedge

**Zovark is the tape recorder for cybersecurity investigations.**

Core flow: **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

The **investigation tape** is the central recorded object — raw evidence, timeline, findings, verdict, EDR handoff record, rollback plan, replay state, and audit references travel together. The **EDR handoff** is replayable, evidence-linked, and reversible. (The investigation tape object schema and EDR handoff record schema are out of scope for the MVP-scope document; they are defined separately under their respective architecture sections.)

The first user is a design-partner security team reviewing incident evidence and deciding whether the product is useful in real incident review.

## M0 / Bootstrap

M0 is not customer runtime. M0 must produce enough repository evidence to start implementation without ambiguous architecture claims:

- ADR and invariant indexes are present and internally consistent.
- Existing schemas and schema examples validate under repository scripts.
- Referenced scripts are either present and executable or labeled as planned deliverables.
- Claim-provenance rules exist.
- MVP scope and out-of-scope items are explicit.
- No customer-facing document contains unbacked hypothesis claims.

## Design-Partner MVP

The MVP includes:

- Tenant-scoped ingestion of sample security data.
- Recorded investigation object containing raw evidence references, model/tool I/O records when used, timeline, findings, verdict/conclusion, and policy snapshot.
- Recorded-output replay that uses stored records and does not call live inference.
- Customer review of raw evidence, reconstructed timeline, grouped incident/campaign, findings, verdict/conclusion, and proposed handoff if present.
- Audit trail for investigation creation, review, replay, and handoff decision.
- Explicit approval before any external action. No fully autonomous external action is in MVP.

## Explicitly Out Of MVP

- Research Pipeline runtime candidate generation.
- Fully autonomous action execution.
- Cross-region disaster recovery guarantees.
- Public plugin ecosystem.
- General-purpose security data platform positioning.
- Benchmark-backed capacity, latency, false-positive, or accuracy claims unless measured artifacts are added.

## Post-MVP

- Research Pipeline runtime (currently M6).
- Sigma false-positive governance (currently M9).
- Air-gap operational proof (currently M10).
- Customer-accessible source mirrors and broader release-channel automation.

## GA

GA requires runtime enforcement evidence for tenant isolation, replay, audit chain, deletion/retention, DR restore-gap handling, supply-chain update verification, and customer observability. This patch tree does not contain that evidence.
