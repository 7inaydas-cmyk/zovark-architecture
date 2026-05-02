# MSSP / SOC Operator Outreach — Customer Discovery

**Goal:** Find MSSP, MDR, and enterprise SOC operators who feel the gap between
AI-recommended response actions and the evidence/approval record that should exist
before those actions are taken.

**Not a sales call.** This is a discovery conversation. We want to understand
whether the problem is real, how painful it is, and whether a replayable proof
package would be useful enough to pilot.

---

## 1. Target persona list

### Primary targets

**MSSP / MDR operations lead**
- Title: VP of Operations, Director of SOC Operations, Head of MDR, SOC Manager
- Company size: 20–500 analysts; serves 50+ clients
- Pain signal: clients in regulated industries (financial services, healthcare,
  critical infrastructure) asking for documented approval trails; post-incident
  reviews where the approval record was reconstructed from memory or tickets
- Where to find: LinkedIn (search "SOC Manager MSSP", "MDR Operations Director"),
  SANS community, MSSPAlert, industry events (RSA, mWISE, SANS SOC Summit)

**Enterprise SOC manager (in-house)**
- Title: SOC Manager, Director of Security Operations, VP of Cyber Defense
- Company size: 500+ employees; regulated industry
- Pain signal: internal audit findings about AI-assisted response decisions;
  compliance team asking for evidence of process, not just outcome; false-positive
  incidents that required post-hoc justification
- Where to find: LinkedIn, CISO community forums, local ISAC chapters

**Compliance-aware CISO at an MSSP**
- Title: CISO, VP of Security, Chief Security Officer
- Pain signal: NIS2 / DORA / SEC AI guidance creating new documentation
  requirements; client contracts requiring audit trails for automated actions
- Where to find: LinkedIn, CISO peer groups, MSSP-focused events

### Secondary targets (for referrals and context)

**SOC analyst (tier 2 / tier 3)**
- The person who actually clicks approve on high-risk actions
- Useful for understanding the approval workflow at ground level
- Reach through their manager; do not cold-outreach analysts directly

**Incident response lead**
- Deals with the aftermath when an approved action turns out to be a false positive
- Useful for understanding the reversal and recovery pain
- Title: IR Lead, Head of Incident Response, Principal IR Consultant

---

## 2. LinkedIn message

**Character limit target: under 300 characters for the connection request note,
under 600 for the follow-up message.**

### Connection request note (if not already connected)

> Hi [Name] — I'm building tooling for SOC approval workflows and would love to
> ask you two questions about how your team handles high-risk response decisions.
> Happy to keep it to 15 minutes. — [Your name]

### Follow-up message (after connection accepted, or as a cold InMail)

> Hi [Name],
>
> I'm working on a tool that creates a replayable evidence package for high-risk
> SOC response decisions — things like host isolation or account disablement —
> before the action is approved.
>
> The specific problem I'm trying to understand: when your team approves one of
> those actions, what evidence exists in a structured, verifiable form? And if a
> client or auditor asks six months later why you took that action, what do you
> show them?
>
> I'm not selling anything. I'm trying to understand whether this is a real gap
> for teams like yours. Would you be open to a 20-minute call?
>
> [Your name]

---

## 3. Email

**Subject line options (A/B test these):**

- `Before you isolate a host — what's in the approval record?`
- `Audit trail for AI-assisted SOC decisions`
- `Quick question about your high-risk response approval process`

---

**Email body:**

Hi [Name],

I'm building Zovark — a tool that creates a replayable proof package for high-risk
SOC response decisions before they're approved.

The problem I'm trying to validate: when your team approves isolating a host or
disabling a user account, is there a structured record of the evidence that
justified it, who approved it, and whether the action could be reversed? And if a
client or regulator asks six months later, can you replay the reasoning?

I'm not pitching a product. I'm trying to understand whether this is a real gap
for MSSP and SOC teams, and if so, what form a solution would need to take to be
useful in your workflow.

I have a working demo — one command, no credentials, produces an approval-required
action card with evidence hashes, a deterministic verdict, a reversal plan, and a
replayable proof package. I can send you the output bundle or walk you through it
in 20 minutes.

Would a short call this week or next work?

[Your name]
[Title]
[Contact]

---

**Follow-up (5 days later, if no reply):**

Hi [Name],

Quick follow-up. The core question I'm trying to answer:

When your SOC approves a high-risk response action — host isolation, account
disablement — could you prove the reasoning to a client or auditor six months later?

If that's a gap you're feeling, I'd like to understand it better. 20 minutes.

[Your name]

---

## 4. Discovery questions

These are the five questions to ask in the discovery call. Ask them in order.
Let the person talk. Do not interrupt with product features.

---

**Q1. Walk me through the last time you isolated a host or disabled a user account.**

*What you are listening for:* the actual workflow — who initiated it, what triggered
it, how fast it moved, whether it was AI-recommended or analyst-initiated. You want
to understand the sequence of events from alert to action.

*Follow-up probes:*
- Was it AI-recommended or did an analyst initiate it?
- How long did the approval process take?
- Was it a false positive? What happened next?

---

**Q2. What evidence did you need before approving it?**

*What you are listening for:* whether there is a structured evidence review step, or
whether approval is based on the alert summary and analyst judgment. You want to
know if "evidence" means a ticket, a dashboard screenshot, a formal review, or
nothing structured at all.

*Follow-up probes:*
- Was that evidence in a structured, verifiable form, or was it a summary?
- Did you have the raw process events, network flows, or alert fields in front of you?
- Could you have reconstructed exactly what evidence was reviewed if asked later?

---

**Q3. Who had to approve it?**

*What you are listening for:* the approval chain — tier 2 analyst, SOC manager,
client notification, automated policy. You want to understand whether there is a
human in the loop and at what level.

*Follow-up probes:*
- Was the approval recorded anywhere? In a ticket? In a system?
- If a client asked who approved it and when, could you answer that precisely?
- Is there a policy that governs which actions require which level of approval?

---

**Q4. Could you prove the reasoning later?**

*What you are listening for:* whether the answer is "yes, here is the record" or
"we'd have to reconstruct it from tickets and memory." This is the core pain signal.

*Follow-up probes:*
- Has a client or auditor ever asked you to justify a response action after the fact?
- What did you show them?
- Was there ever a case where you couldn't fully reconstruct why an action was taken?

---

**Q5. Would a replayable evidence and approval package be useful enough to pilot?**

*Ask this only after the first four questions. Do not lead with it.*

*Frame it as:* "Based on what you've described — [reflect back their specific pain
point] — would it be useful to have a structured package that records the evidence,
the verdict, the approval, and the reversal plan before the action is dispatched,
and that can be replayed later to verify the reasoning?"

*What you are listening for:* whether they immediately see the use case, whether
they push back on the format, whether they name a specific workflow it would fit
into, or whether they say "we already have this" (disqualifying).

---

## 5. Strong positive signals

These responses indicate a real, felt problem worth pursuing:

- **"We reconstruct it from tickets."** The approval record exists only as a
  narrative assembled after the fact. This is the core gap.

- **"A client asked us to justify an isolation and it took us two days to pull
  together the evidence."** Direct experience of the pain.

- **"Our compliance team is asking us for documented approval trails for AI-assisted
  actions and we don't have a good answer."** Regulatory pressure creating urgency.

- **"We had a false positive that isolated a production server and the client wanted
  to know exactly what happened."** Reversal and accountability pain.

- **"We're getting asked about NIS2 / DORA / SEC AI guidance and we're not sure
  what we need to produce."** Compliance uncertainty creating a buying trigger.

- **"The analyst just clicks approve based on the alert. There's no formal evidence
  review."** Workflow gap that Zovark directly addresses.

- **"We have a policy but no system that enforces it at approval time."** Policy
  exists but is not operationalized — Zovark is the operationalization layer.

- **"I'd want to see the reversal plan before approving something like that."**
  Direct articulation of the value proposition.

---

## 6. Weak or disqualifying signals

These responses suggest the problem is not felt, the fit is wrong, or the timing
is off:

- **"We already have a SOAR that handles this."** Ask what the SOAR records at
  approval time. If they can describe a structured evidence package with hashes and
  a reversal plan, this is a genuine disqualifier. If they describe a ticket with
  an alert summary, it is not.

- **"Our analysts don't approve high-risk actions — everything is automated."**
  This is a different workflow. Autonomous response is not our current product.
  Note for future reference; do not pursue as a design partner now.

- **"We don't do host isolation or account disablement — we just alert."**
  Wrong persona. They are a detection-only shop. Move on.

- **"Compliance isn't a concern for our clients."** Unlikely for regulated-industry
  MSSPs, but if true, the urgency driver is absent. The problem may still exist but
  the buying trigger is weaker.

- **"We have a dedicated GRC team that handles all of this."** The GRC team records
  policies and controls, not per-action evidence packages. This is usually a
  misunderstanding of what Zovark does — clarify. But if they genuinely believe the
  GRC team covers it, the champion is in the wrong place.

- **"We'd need this to integrate with [specific SIEM/SOAR] before we could use it."**
  Note the integration requirement. This is not disqualifying — it is a design
  input. But if the integration is a hard prerequisite and the timeline is
  incompatible, park for later.

---

## 7. Pilot / design-partner ask

Use this ask at the end of a call where you heard at least two strong positive
signals.

---

**Verbal ask:**

> "Based on what you've described, I think there's a real fit here. We're looking
> for two or three design partners — MSSP or SOC teams who will review the action
> card and proof package format with us and tell us whether it fits their approval
> workflow.
>
> It's not a production deployment. You'd receive the output bundle from a demo run,
> review it with your team, and give us feedback on the format, the fields, and
> what's missing. One or two sessions, maybe an hour total.
>
> Would that be something your team would be willing to do?"

---

**Written follow-up (send within 24 hours of the call):**

Subject: `Zovark design partner — next step`

Hi [Name],

Thanks for the conversation. Based on what you described — [one sentence reflecting
their specific pain point back to them] — I think Zovark could be directly useful
for your team.

Here is what I'm proposing:

1. I send you the output bundle from our demo run — the action card, the proof
   package, and the proof report.
2. You review it with [the relevant person on their team — analyst, compliance,
   operations lead].
3. We do a 30-minute follow-up call where you tell us what fits, what doesn't, and
   what's missing.

No production deployment. No integration work. Just a structured review of the
format and a conversation about whether it would be useful in your approval workflow.

If that sounds reasonable, I'll send the bundle today.

[Your name]

---

## Notes on tone

- Do not lead with the product. Lead with the problem.
- Do not use the word "platform." It signals scope creep.
- Do not say "AI-powered" or "AI-driven" about Zovark. The point is that Zovark
  makes AI recommendations safe to act on — it is not itself an AI product.
- Do not claim production readiness. The honest framing is: "We have a working
  demo that produces the full proof package from a static sample. We are looking
  for design partners to validate the format before we build the live integration."
- If they ask about pricing, say: "We are not at that stage yet. Design partners
  get early access and direct input into the product. We will talk about pricing
  when we have a production-ready integration."
