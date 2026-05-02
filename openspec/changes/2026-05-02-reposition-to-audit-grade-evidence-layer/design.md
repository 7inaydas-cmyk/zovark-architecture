## Context

The internal architecture is frozen at rc3. The investigation tape, evidence ledger,
timeline, findings, verdict, EDR handoff, replay report, and audit chain are all
correct and unchanged. The problem is purely external: the current wedge
("tape recorder") is an engineering metaphor that does not communicate customer
value to a YC partner, MSSP buyer, or SOC manager.

The reposition is a controlled documentation change. It introduces a two-layer
wedge model: one internal statement for engineering documents, one external
statement for everything customer-facing. No runtime capabilities change.

## Goals / Non-Goals

**Goals:**

- One external canonical statement that lands with a non-technical evaluator.
- One customer one-liner that names the concrete value before the SOC acts.
- `customer-report.md` leads with the EDR action card (recommended action, evidence,
  approval status, reversibility), not with the tape ID.
- Three new documents: YC positioning, Slice 001 demo script, MSSP outreach.
- All existing architecture enforcement scripts continue to pass.

**Non-Goals:**

- Changing any internal architecture spec (`investigation-tape`, `edr-handoff`,
  `replay-and-audit`, `vault-authorization`).
- Changing Slice 001 implementation scope (same 9 output artifacts, same modules,
  same tasks).
- Adding live EDR, autonomous action, Sigma, SIEM, UI, vault runtime, or
  multi-tenancy.
- Rewriting the architecture objects or ADRs.

## Decisions

### Two-layer wedge model

The `product-wedge` spec now governs two canonical statements:

1. **Internal** — "Zovark is the tape recorder for cybersecurity investigations."
   Governs: `openspec/specs/`, `architecture/`, ADRs, engineering specs.

2. **External** — "Zovark is the audit-grade evidence layer for AI-assisted SOC
   response." Governs: customer-facing docs, investor materials, demo scripts,
   outreach.

**Rationale.** A single statement cannot serve both audiences. The tape recorder
metaphor is precise for engineers (immutable record, replay, audit chain) but
opaque to buyers (what does a tape recorder do for my SOC?). The audit-grade
evidence layer framing names the market category (evidence layer), the quality bar
(audit-grade), and the context (AI-assisted SOC response) in one phrase.

### Hero artifact designation

The external hero artifacts are:
- **EDR action card** — `edr-handoff.json`: recommended action, target, evidence
  basis, approval status, reversibility class.
- **Replayable proof package** — `replay-report.json` + `customer-report.md`:
  evidence hashes verified, verdict recomputed, audit chain linked.

The investigation tape is the internal proof substrate. It is not hidden — it is
listed in the artifacts section of `customer-report.md` — but it is not the first
thing a customer sees.

**Rationale.** A SOC manager reviewing a Zovark output wants to know: what action
is recommended, why, who approved it, and can I verify it? The action card answers
the first three; the proof package answers the fourth. The tape is the mechanism
that makes both possible, but it is not the value proposition.

### `customer-report.md` section order

New order:
1. External wedge statement (one line)
2. Recommended Action (EDR action card) — action, target, approval status,
   reversibility
3. Verdict — value, evidence basis, model contribution
4. Evidence and Findings — table
5. Approval Path — mode, status, authorization ref
6. Replayable Proof — replay result, hashes verified, verdict recomputed
7. Audit Chain — entries, chain integrity
8. Internal Proof Substrate — tape ID, tenant, source alert (moved to near-bottom)
9. Artifacts — list, with hero artifacts first

**Rationale.** The previous order led with the tape ID, which is an internal
identifier. A design partner's first question is "what are you recommending and
why?" — not "what is the tape ID?". Moving the action card to the top answers
that question immediately.

### YC positioning doc

`docs/yc-positioning.md` covers:
- One-line description (external wedge)
- Problem (SOC teams act on AI recommendations without audit-grade evidence)
- Solution (Zovark produces an approval-required action card + replayable proof
  package before any EDR action)
- Why now (AI-assisted SOC is mainstream; audit and compliance requirements are
  catching up)
- Traction hook (Slice 001 demo: one command, one static sample, full proof package)
- Ask (design partner access, MSSP pilot)

### Slice 001 demo script

`docs/slice-001-demo-script.md` is a step-by-step walkthrough for a 10-minute
design-partner or YC demo:
1. Show the problem (AI recommends isolate_host — where's the evidence?)
2. Run the command (one line, no credentials, no network)
3. Open `customer-report.md` — action card first
4. Open `edr-handoff.json` — show the 14 fields, approval gate, rollback plan
5. Open `replay-report.json` — show `state: succeeded`, hashes verified
6. Explain what this means for compliance and audit

### MSSP outreach doc

`docs/mssp-outreach.md` is a one-page cold outreach template for MSSP buyers:
- Subject line and opening hook
- Problem statement (one paragraph)
- What Zovark produces (action card + proof package, bullet list)
- What it does not do (no autonomous action, no credentials required for demo)
- Call to action (30-minute demo, Slice 001 output bundle attached)

## Risks / Trade-offs

- **Risk:** "audit-grade" sets a quality expectation that Slice 001 does not fully
  meet (no cryptographic root signature, no production vault). → **Mitigation:**
  the demo script and outreach doc explicitly state "bootstrap mode" and "root
  signing deferred to M1+". The claim is about the architecture's design intent,
  not the current implementation state.
- **Risk:** two canonical statements create maintenance burden. → **Mitigation:**
  the `product-wedge` spec governs both; any future change to either requires a
  `MODIFIED Requirements` change through the same process.
- **Trade-off:** "tape recorder" disappears from external materials. Accepted: it
  remains the internal engineering metaphor and is preserved in all architecture
  documents. Engineers will still use it; customers will not see it as the headline.
