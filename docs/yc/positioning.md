# Zovark — YC Positioning

> This document is YC application and investor positioning material.
> It is not architecture source of truth.
> Internal architecture is governed by `openspec/specs/` and `architecture/`.

---

## 1. One-liner

Zovark helps SOC and MSSP teams safely approve high-risk response actions by
producing replayable evidence, deterministic verdicts, approval-required EDR action
cards, and reversal/recovery plans.

---

## 2. Thirty-second explanation

When an AI system recommends isolating a host or disabling a user account, someone
in the SOC has to click approve. Right now that person has a ticket number, an alert
summary, and a gut feeling. They have no structured evidence package, no documented
approval path, and no way to replay the reasoning later if a regulator or client
asks why.

Zovark sits between the AI recommendation and the EDR action. It assembles the
evidence, derives a deterministic verdict, produces an approval-required action card
with a reversal plan, and creates a replayable proof package. Nothing dispatches
without human approval. Everything is recorded and verifiable.

---

## 3. Problem

AI-assisted SOC response is already mainstream. CrowdStrike, SentinelOne, Microsoft
Defender, and a growing set of AI SOC platforms all generate automated or
AI-recommended response actions. SOC teams and MSSPs are acting on those
recommendations every day.

The gap is not the AI. The gap is what happens after the AI recommends something:

**No structured evidence record.** The AI produced a recommendation. The analyst
approved it. But the evidence that justified the recommendation — the specific
process events, network flows, and alert fields — is not captured in a structured,
verifiable form. It lives in a ticket, a dashboard screenshot, or the analyst's
memory.

**No documented approval path.** Who approved the action? When? Against what policy
version? What was the authorization scope? These questions matter for compliance,
for post-incident review, and for client reporting. The answers are usually
unavailable or reconstructed after the fact.

**No reversal plan at approval time.** Before an analyst approves isolating a host,
they should know: can this be reversed automatically, does it require manual steps,
or is it effectively irreversible? That information is rarely surfaced at the moment
of decision.

**No replay.** If a client or regulator asks "why did you take that action six months
ago?", the answer should be a verifiable proof package, not a ticket number. Today
it is almost always the ticket number.

This is not a future problem. It is happening in every SOC that has deployed
AI-assisted detection or response tooling.

---

## 4. Why now

Three forces are converging in 2025–2026:

**AI-assisted SOC is past the early-adopter phase.** The major EDR vendors have
shipped AI-driven response recommendations. A new generation of AI SOC platforms
(autonomous SOC, AI analysts) is in production at enterprise and MSSP customers.
The tooling exists. The audit layer does not.

**Compliance requirements are catching up to AI.** NIS2 (effective October 2024),
DORA (effective January 2025), and emerging SEC guidance on AI in financial services
all require documented, auditable decision trails for automated or AI-assisted
actions. MSSPs serving regulated industries — financial services, healthcare,
critical infrastructure — are being asked by their clients for evidence of process,
not just evidence of outcome.

**Liability is shifting from "did the AI make a mistake?" to "did you have a
process?"** When an AI-recommended action causes a business disruption — a false
positive that isolates a production server during a trading window — the legal and
contractual question is no longer purely technical. It is: did the MSSP have a
documented, auditable approval process? Did they know the action was reversible
before they approved it? Zovark is that process.

**The window for a purpose-built evidence layer is open now.** The EDR vendors are
focused on detection and response, not on audit infrastructure. The AI SOC platforms
are focused on automation, not on the approval and evidence layer that makes
automation safe. No incumbent owns this space.

---

## 5. First customer

The first customer is an MSSP or enterprise SOC team that:

- Has deployed or is evaluating AI-assisted detection or response tooling.
- Serves regulated-industry clients (financial services, healthcare, critical
  infrastructure) who ask for documented approval trails.
- Has experienced at least one incident where a response action was questioned
  after the fact — by a client, an auditor, or internally.
- Has 10 or more analysts, enough volume that the approval and evidence gap is felt
  as a workflow problem, not just a theoretical risk.

The first design-partner conversation is not a sales call. It is: here is the
approval-required action card and proof package that Slice 001 produces from a
static EDR sample. Does this format match what your SOC workflow needs? What is
missing? What would make this useful in your approval process today?

---

## 6. What we are building first

**Slice 001 — the static proof-of-concept pipeline:**

One command. One static EDR-like JSON sample. No credentials. No network. Produces:

- An approval-required EDR action card (`edr-handoff.json`) — recommended action,
  target, evidence basis, approval gate, reversibility/recovery classification.
- A replayable proof package (`replay-report.json`) — evidence hashes verified,
  verdict recomputed deterministically, audit chain linked.
- A human-readable proof report (`customer-report.md`) — the artifact a SOC analyst
  or auditor actually reads.

The internal substrate is an investigation tape: an immutable, hash-linked record
that captures the evidence ledger, timeline, findings, verdict, and handoff
reference. The tape is what makes replay possible.

This slice exercises every governing architecture spec. It proves the wedge: a
customer can inspect and replay why Zovark recommended an EDR action.

**After Slice 001, in order:**

- Live EDR alert ingestion (static file → live feed from one EDR vendor).
- Vault runtime for authorization records (replacing the bootstrap placeholder).
- Design-partner pilot: one MSSP running Zovark on real alerts in
  approval-required mode.
- Multi-tenant deployment.

---

## 7. What we are not building first

- **Live EDR dispatch.** Zovark produces approval-required action cards. It does not
  dispatch actions autonomously. Autonomous mode is a future capability, explicitly
  deferred. Every action requires human approval in the current product.
- **AI model inference.** Slice 001 findings are rule-driven. The architecture
  supports model-contributed findings, but the proof package and replay work
  identically whether or not a model was involved. We are not building an AI model.
  We are building the evidence and approval layer that makes AI recommendations safe
  to act on.
- **SIEM or log aggregation.** Zovark does not aggregate logs or generate Sigma
  rules. It produces a per-investigation proof package from structured EDR input.
- **Compliance dashboards or reporting portals.** The proof package is the
  compliance artifact. The dashboard is a future layer.
- **Multi-vendor EDR integration.** The first live integration targets one EDR
  vendor. Vendor-agnostic abstraction comes after the first pilot.

---

## 8. Why incumbents do not solve this

**EDR vendors (CrowdStrike, SentinelOne, Microsoft Defender)** are focused on
detection accuracy and response speed. Their audit logs record what happened, not
why a specific recommendation was made or what evidence justified it. They do not
produce structured, replayable evidence packages. They do not surface reversal plans
at approval time. Audit is not their product.

**AI SOC platforms (autonomous SOC vendors, AI analyst tools)** are optimizing for
automation and analyst efficiency. Their value proposition is reducing the number of
decisions a human has to make. The approval and evidence layer that makes those
decisions auditable is not their focus — it is friction in their funnel.

**SIEM vendors (Splunk, Microsoft Sentinel, Elastic)** aggregate and correlate
events. They can tell you what happened. They cannot tell you why a specific
AI-recommended action was approved, what evidence was presented at approval time,
or whether the action was reversible. They are not structured around the
per-investigation proof package.

**GRC and compliance platforms** record policies and controls. They do not integrate
with the real-time SOC workflow or produce per-action evidence packages.

The gap is structural: no incumbent is positioned to own the evidence and approval
layer between AI recommendation and EDR action. It requires deep integration with
the SOC workflow, a purpose-built data model for investigation evidence, and a
replay architecture that is independent of the AI model that produced the
recommendation.

---

## 9. Why deterministic replay is the moat

The core technical property that makes Zovark defensible is **deterministic replay**:
given the same recorded inputs, the same verdict is always produced, and any auditor
can verify this without access to the original AI model, the original analyst, or
the original environment.

This is harder to build than it sounds, and it is not something that can be bolted
onto an existing system:

**It requires a purpose-built data model.** The investigation tape captures not just
the outcome but the exact inputs — the evidence entries with content hashes, the
recorded model and tool I/O, the timeline of decisions. Every field that contributed
to the verdict is recorded. Every field that did not is excluded from the replay
computation.

**It requires canonical serialization.** The audit chain entries are hashed using a
deterministic canonical JSON serialization. Two independent implementations produce
byte-identical output. This is what makes the chain independently verifiable — not
just by Zovark, but by any auditor with the spec.

**It requires a no-live-call replay mode.** Replay in `recorded_output` mode makes
no network calls, invokes no model, and reads no external state. The proof package
is self-contained. An auditor can verify it offline, years later, without any
dependency on Zovark's infrastructure being available.

**It creates a compounding advantage.** Every investigation tape is a training
signal for the verdict derivation rules. Every replay that succeeds is evidence that
the rules are stable. Every replay that produces a mismatch is a signal that
something changed — in the evidence, in the rules, or in the environment. Over time,
the corpus of verified tapes becomes a proprietary dataset that no competitor can
replicate without running the same investigations.

The moat is not the AI. The moat is the verified, replayable record of every
AI-assisted decision, accumulated over time, that makes Zovark the system of record
for SOC response evidence.

---

## 10. Founder-fit paragraph

*[Placeholder — to be written by the founder(s). Should address: direct experience
with the SOC approval and audit gap, either as a practitioner, a vendor, or a
customer; specific incidents or conversations that made the problem concrete; why
this team is the right team to build the evidence and approval layer for AI-assisted
SOC response; and what unfair advantage — technical, domain, or network — the
founders bring to this specific problem.]*

---

## 11. YC application draft — "What are you making?"

Zovark is the audit-grade evidence layer for AI-assisted SOC response.

When an AI system recommends isolating a host or disabling a user account, a SOC
analyst has to approve it. Today that analyst has an alert summary and a gut feeling.
They have no structured evidence package, no documented approval path, and no way to
replay the reasoning later.

Zovark sits between the AI recommendation and the EDR action. It assembles the
evidence from the alert, derives a deterministic verdict using a recorded rule set,
and produces an approval-required action card that shows the analyst exactly what
action is recommended, what evidence justifies it, whether it can be reversed
automatically or requires manual recovery, and what the authorization scope is.
Nothing dispatches without human approval.

After the analyst approves or rejects, Zovark creates a replayable proof package: a
cryptographically-linked record that lets any auditor verify, months or years later,
that the verdict was correct given the evidence at the time. The replay makes no
live calls — it is self-contained and verifiable offline.

The first version runs on a static EDR sample with no live integrations. The
architecture is designed for live EDR feeds, vault-backed authorization, and
multi-tenant MSSP deployment. We are building toward a design-partner pilot with one
MSSP running Zovark on real alerts in approval-required mode.

The market is every MSSP and enterprise SOC team that has deployed AI-assisted
response tooling and is now being asked — by clients, auditors, or regulators — to
show their work.
