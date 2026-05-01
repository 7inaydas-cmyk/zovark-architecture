# Zovark One-Page Architecture

Status: `architecture-rc3` (evidence-backed freeze)
Purpose: build-planning map, derived from frozen specs. Not a new source of truth.
Source specs: `openspec/specs/`. Source objects: `architecture/objects/`.

## 1. Product wedge

**Zovark is the tape recorder for cybersecurity investigations.**

Core flow: **EDR alerts → investigation tape → replayable evidence → deterministic verdict → verified EDR handoff → rollback/reversal record.**

## 2. First MVP build slice

Smallest path that exercises every governing spec. Per rc3 scorecard.

**Input:** one static EDR-like JSON sample.
**Output:** 1 investigation tape, 1 timeline, 1 evidence ledger, 1 verdict, 1 EDR handoff recommendation (`approval_required` mode), 1 replay report.

**Out of slice:** live EDR API; autonomous action; Sigma/SIEM publication; multi-tenant production deployment; full UI; production credential vault runtime; production DR.

## 3. Core architecture objects

### Investigation Tape (`investigation-tape`)
System-of-record umbrella for one investigation. Immutable once closed.
Fields: `tape_id`, `tenant_id`, `created_at`, `schema_version`, `source_alert_ref`, `raw_evidence[]` (evidence ledger), `timeline[]`, `findings[]`, `verdict`, `recorded_io[]` (when models/tools used), `handoff_ref`, `audit_ref`. Lifecycle: `recording → closed` (one-way; no `replaying` tape state — replay status lives in `replay-and-audit`).

### Evidence ledger (`investigation-tape.raw_evidence[]`)
Immutable list inside the tape. Each entry: `evidence_id`, `hash` (SHA-256+), `source_type`, `ingested_at`, `retention_class` (post-MVP).

### Timeline (`investigation-tape.timeline[]`)
Ordered event log inside the tape. Each event: `event_type`, `at`, `actor`, `evidence_refs[]`, `decision_contribution`. Non-decreasing timestamp order.

### Verdict (`investigation-tape.verdict`)
Deterministic. `value` ∈ {`benign`, `suspicious_unconfirmed`, `confirmed_malicious`, `inconclusive_insufficient_evidence`}. Plus `evidence_refs[]`, `model_contribution`, `signing_tag`, `set_at`. Replay must recompute the same value.

### EDR Handoff Recommendation (`edr-handoff`)
Separate record referenced from the tape via `handoff_ref`. 14 fields: identity (`handoff_id`, `tenant_id`, `tape_ref`), action+target (typed enums), `evidence_refs`, `policy_snapshot`+version, `approval_mode` (MVP: `approval_required` only), `authorization_record_ref`, `idempotency_key`, `execution_result`, `rollback_plan` (class: automatic/manual_documented/irreversible), `audit_ref`, `replay_linkage`.

### Replay Report (`replay-and-audit`)
Combined artifact: `replay_state` (per-replay) + audit chain entry of type `tape_replayed`. Fields: `replay_id`, `tape_ref`, `mode` (MVP: `recorded_output`), pins (`schema_pin`, `tool_catalog_pin`, `model_versions_pin`), `state` ∈ {succeeded, mismatch, failed}, `mismatch_details` if any. No live LLM/tool calls.

## 4. Runtime path for first slice

1. Load static EDR-like JSON sample.
2. Normalize into evidence entries (assign `evidence_id`, compute `hash`, set `source_type`/`ingested_at`).
3. Create the tape (`recording` state); fill identity fields; append evidence entries to `raw_evidence`.
4. Build timeline events from the evidence; mark `decision_contribution`.
5. Derive evidence-backed `findings` (rule-driven; `model_contribution: false` for the first slice).
6. Set `verdict` deterministically from findings; emit signing tag.
7. Build the `edr-handoff` record (`approval_mode: approval_required`; rollback plan class set per action type).
8. Seal the tape (`recording → closed`); write the audit chain entry; sign root (or stub root for first slice).
9. Run replay against the closed tape; emit the replay report (`tape_replayed` audit entry; verify hashes; recompute verdict).
10. Export the tape + replay report bundle for design-partner review.

## 5. Trust boundaries (first slice)

- No live EDR credentials — sample input only.
- No autonomous action — `approval_required` is the only mode permitted.
- No live LLM during replay — `recorded_output` mode only.
- No customer production data; no cross-tenant runtime.
- No production claims of enforcement — the tape and replay report are the evidence; nothing else.

Later: vault runtime authorization (`vault-authorization` capability); signed EDR action authorization; production tenant isolation; production audit chain with root-signing; DR + restore-gap (`disaster_recovery_restore_completed` event).

## 6. Deferred architecture

Per rc3 scorecard `PASS-with-explicit-DEFERRAL` annotations: M2 control-plane DR sketch (ARCH-P2-002, owner: architect); M3 vault IPC schemas + `check_vault_ipc_contract.py` (owner: schema-owner); post-apply baseline-ADR cross-link verification (script ready, awaits v3.2.3.5 baseline merge).

Also out of MVP: live EDR vendor integration; credential vault runtime; autonomous response; multi-tenant SaaS; Sigma generation; SIEM publication; DR drills; customer-facing dashboards.

See `architecture/review/release-candidate-scorecard.md` for owner/milestone/acceptance per item.

## 7. Build rule

The first implementation must prove the wedge:

> Can a customer inspect and replay why Zovark recommended an EDR action?

If yes — the slice is useful, and the architecture is productized.
If no — the architecture is unproductized; iterate before broadening scope.
