# Slice 001 — Demo Script

**Audience:** design partners, YC partners, MSSP evaluators
**Duration:** 10 minutes
**Prerequisites:** Python 3.11+, repo cloned, `samples/edr-sample-001.json` present

---

## Setup (before the call, 2 minutes)

Run the command once so the output is ready:

```bash
python -m zovark.slice001 \
  --input samples/edr-sample-001.json \
  --output out/ \
  --tenant-id tenant-001
```

Confirm `out/customer-report.md` exists and `replay_state.state` is `succeeded`
in `out/replay-report.json`.

---

## The demo (10 minutes)

### Minute 1 — The problem

> "AI is recommending that your SOC isolate this workstation. Before anyone acts,
> I want to show you what Zovark produces."

Open a terminal. Show the input:

```bash
cat samples/edr-sample-001.json
```

Point out: one EDR alert, one process event, a host name. This is the raw signal.

> "Right now, your SOC gets this alert and an AI recommendation. What they don't
> get is the evidence package, the approval record, or any way to replay the
> reasoning later."

---

### Minute 2 — Run the command

```bash
python -m zovark.slice001 \
  --input samples/edr-sample-001.json \
  --output out/ \
  --tenant-id tenant-001
```

Show the output:

```
Slice 001 complete.
  edr-handoff.json          → out/edr-handoff.json
  replay-report.json        → out/replay-report.json
  customer-report.md        → out/customer-report.md
  ...
Replay: succeeded
```

> "One command. No credentials. No network. No AI model running during replay.
> Let me show you what was produced."

---

### Minutes 3–4 — The action card (`customer-report.md`)

Open `out/customer-report.md`.

> "The first thing your SOC sees is the action card."

Read the top section aloud:

```
## Recommended Action (EDR Action Card)

Action: ISOLATE_HOST
Target: workstation-42.corp.example (host)
Approval required: YES — no action has been dispatched
Reversibility: automatic (release_isolation available)
```

> "The action is recommended. It has not been dispatched. A human must approve it.
> And if it turns out to be a false positive, the reversal is automatic — one API
> call to release the isolation."

Scroll to the verdict:

> "The verdict is CONFIRMED_MALICIOUS. It was derived from two findings: an EDR
> alert and a suspicious process event. No model contributed — this is fully
> rule-driven and deterministic. Same input, same verdict, every time."

---

### Minutes 5–6 — The action card in detail (`edr-handoff.json`)

Open `out/edr-handoff.json`.

Point out:
- `approval_mode: "approval_required"` — the gate
- `authorization_record_ref: "vault://placeholder/bootstrap"` — placeholder for
  now; production vault in M3
- `execution_result.status: "pending"` — nothing has happened yet
- `rollback_plan.reversibility_class: "automatic"` — the safety net
- `evidence_refs` — the specific evidence IDs that justify this action
- `idempotency_key` — if this recommendation is submitted twice, it's a no-op

> "Every field is traceable. The evidence refs link back to the exact bytes that
> were ingested. The rollback plan tells the operator exactly what reversal looks
> like before they approve."

---

### Minutes 7–8 — The proof package (`replay-report.json`)

Open `out/replay-report.json`.

Point out:
- `replay_state.state: "succeeded"`
- `replay_state.mode: "recorded_output"` — no live model calls during replay
- `payload.evidence_hashes_verified: true`
- `payload.verdict_matched: true`
- `prev_entry_hash` linking to the close entry

> "This is the replayable proof. An auditor six months from now can take this
> file, the investigation tape, and the same rule set, and verify that the verdict
> was correct given the evidence at the time. No model needs to be running. No
> credentials needed. The proof is self-contained."

---

### Minute 9 — What this means for compliance

> "When a regulator asks 'why did you isolate that machine?', you open the proof
> package. Here is the evidence. Here is the verdict. Here is the approval record.
> Here is the replay that confirms the reasoning was sound. That's audit-grade."

> "Right now this runs on a static sample. The architecture is frozen and
> evidence-backed. The next step is connecting it to your live EDR feed and
> running it in approval-required mode on real alerts."

---

### Minute 10 — The ask

> "We're looking for three to five design partners who will review the action card
> format and proof package structure with us. You don't need to change anything in
> your stack. We send you the output bundle; you tell us whether this is the right
> format for your SOC workflow and your compliance requirements."

> "Does this solve a real problem for your team?"

---

## Handling common questions

**"Does this require an AI model?"**
No. Slice 001 is fully rule-driven. The architecture supports model-contributed
findings in later slices, but the proof package and replay work identically whether
or not a model was involved.

**"What EDR vendors do you support?"**
The architecture is vendor-agnostic. Slice 001 uses a static sample. Live EDR
integration is M1. We are designing the adapter interface to support CrowdStrike,
SentinelOne, and Microsoft Defender first.

**"What does 'approval required' mean in practice?"**
In Slice 001, it means the action card is produced but nothing is dispatched. In
production, it means a human approval is recorded in the authorization record before
the EDR adapter is called. Autonomous mode is explicitly deferred — we are not
building a system that acts without human review.

**"Can I see the investigation tape?"**
Yes — `out/investigation-tape.json`. It is the internal proof substrate: the
immutable record that contains the evidence ledger, timeline, findings, verdict,
and handoff reference. The action card and proof package are derived from it.

**"What about false positives?"**
The rollback plan is part of every action card. For `isolate_host`, the reversal
is `release_isolation` — automatic, one API call. For actions that are harder to
reverse, the rollback plan documents the manual steps before the action is approved.
