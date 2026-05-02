# MSSP Outreach — Template

**Use:** cold outreach to MSSP security operations leads, SOC directors, and
compliance officers at MSSPs serving regulated industries.

---

## Email template

**Subject:** Audit trail for your AI-assisted SOC recommendations

---

Hi [Name],

Your SOC is probably already acting on AI-generated recommendations — isolate this
host, block this hash, disable this account. The tooling is there. The audit trail
is not.

When a client asks "why did you isolate that machine last Tuesday?", what do you
show them?

We're building Zovark — the audit-grade evidence layer for AI-assisted SOC response.
Before any EDR action is dispatched, Zovark produces:

- **An approval-required action card** — the recommended action, the evidence it
  is based on, the approval gate, and the rollback plan.
- **A replayable proof package** — a cryptographically-linked record that lets any
  auditor verify the verdict was correct given the evidence at the time.

Nothing is dispatched without human approval. Every recommendation is evidence-backed
and replayable. The proof package is the compliance artifact.

We have a working demo — one command, no credentials, no network, produces a full
proof package from a static EDR sample. I can send you the output bundle or walk
you through it in 10 minutes.

Would a 30-minute call this week or next work?

[Your name]

---

## Follow-up (if no reply after 5 days)

**Subject:** Re: Audit trail for your AI-assisted SOC recommendations

---

Hi [Name],

Quick follow-up. The core question we're trying to answer for MSSPs:

> When a regulator or client asks "why did you take that action?", can you show
> them the evidence, the verdict, the approval record, and a replay that confirms
> the reasoning was sound?

If that's a gap you're feeling, I'd like to show you what we've built.

[Your name]

---

## Talking points for the call

**Opening (2 minutes)**

> "Tell me about your current process when an AI tool recommends an EDR action.
> What does the approval workflow look like? What do you give a client when they
> ask for the audit trail?"

Listen for: manual approval steps, lack of structured evidence record, compliance
pressure from regulated clients (financial services, healthcare, critical
infrastructure).

**Problem framing (2 minutes)**

> "The pattern we're seeing is: AI recommendation → human clicks approve → action
> taken → no structured record of why. When NIS2 or DORA asks for a documented
> decision trail, the answer is usually a ticket number and a screenshot."

**Solution (3 minutes)**

> "Zovark sits above your EDR layer. When an alert comes in, it produces an
> approval-required action card — the recommended action, the evidence it's based
> on, the approval gate, and the rollback plan. Nothing dispatches until a human
> approves. The approval is recorded. The evidence is hashed. The verdict is
> replayable."

> "The proof package is self-contained. An auditor can verify it without running
> any model, without credentials, without access to your live environment."

**Demo offer (1 minute)**

> "I can send you a sample output bundle right now — action card, proof package,
> the full artifact set. Or I can walk you through it on screen. Which would be
> more useful?"

**Ask (2 minutes)**

> "We're looking for three to five design partners who will review the action card
> format and proof package structure with us. You tell us whether this fits your
> SOC workflow and your compliance requirements. We incorporate your feedback before
> we build the live EDR integration."

---

## Qualification criteria

Prioritize MSSPs that:
- Serve regulated industries (financial services, healthcare, critical infrastructure)
- Have deployed or are evaluating AI-assisted detection/response tools
- Have received compliance questions about AI decision trails from clients or auditors
- Have 10+ analysts in their SOC (enough volume to feel the audit gap)

Deprioritize:
- Pure MDR providers with no SOC workflow (they won't have the approval gap)
- MSSPs with no AI tooling yet (too early in the adoption curve)
- MSSPs that have built their own evidence layer (they are a reference, not a prospect)

---

## What to attach

Attach `out/customer-report.md` from a Slice 001 run. It is the artifact the
prospect will actually read. Lead with the action card section. Do not attach the
full JSON files in the first outreach — offer them as a follow-up.
