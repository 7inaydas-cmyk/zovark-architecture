# Slice 001 — Demo Script

**Story:** Before approving host isolation, here is the proof package.

**Audience:** YC partner, MSSP operations lead, SOC manager
**Duration:** 12 minutes
**Format:** terminal + file viewer, no slides required
**Prerequisites:** Python 3.11+, repo cloned, output already generated

---

## Before the call — setup (2 minutes, done in private)

Run the pipeline once so all output is ready:

```bash
python -m zovark.slice001 \
  --input samples/edr-sample-001.json \
  --output out/ \
  --tenant-id tenant-001
```

Confirm the terminal printed `Replay: succeeded`.

Open these files in a viewer so you can switch to them instantly:
- `samples/edr-sample-001.json`
- `out/edr-handoff.json`
- `out/evidence-ledger.json`
- `out/verdict.json`
- `out/replay-report.json`
- `out/customer-report.md`

---

## The demo

---

### Step 1 — The noisy EDR sample (1 minute)

**What to show:** `samples/edr-sample-001.json`

```json
{
  "alert_id": "alert-20260501-001",
  "alert_type": "edr_alert",
  "host": "workstation-42.corp.example",
  "timestamp": "2026-05-01T10:00:00Z",
  "severity": "high",
  "description": "Suspicious PowerShell execution detected",
  "process_events": [
    {
      "event_id": "pe-001",
      "event_type": "process_event",
      "process_name": "powershell.exe",
      "command_line": "powershell.exe -EncodedCommand <base64>",
      "pid": 4812,
      "parent_pid": 1024,
      "timestamp": "2026-05-01T10:00:01Z"
    }
  ]
}
```

**Narration:**

> "This is the raw EDR alert. High severity. Suspicious PowerShell execution on
> workstation-42. An encoded command — the kind of thing that shows up in
> living-off-the-land attacks.
>
> Your AI system sees this and recommends: isolate the host.
>
> Right now, your analyst gets this alert and a recommendation. What they don't get
> is a structured evidence package, a documented approval path, or any way to
> replay the reasoning later. They click approve on instinct.
>
> Let me show you what Zovark produces instead."

---

### Step 2 — The EDR action card (2 minutes)

**What to show:** `out/edr-handoff.json` — scroll to the top, show these fields:

```json
{
  "handoff_id": "handoff-...",
  "action_type": "isolate_host",
  "target": {
    "kind": "host",
    "identifier": "workstation-42.corp.example",
    "validated_at": "2026-05-01T10:05:01Z"
  },
  "approval_mode": "approval_required",
  "execution_result": {
    "status": "pending",
    "reason": "recommendation_only_no_dispatcher_in_slice_001"
  }
}
```

**Narration:**

> "This is the EDR action card. It is the first thing your analyst sees.
>
> The recommended action is `isolate_host`. The target is
> `workstation-42.corp.example`. The approval mode is `approval_required` — nothing
> has been dispatched. Status is `pending`.
>
> This is not a log entry after the fact. This is the structured decision artifact
> that exists *before* anyone clicks approve. The analyst can read it, review it,
> and reject it if something looks wrong.
>
> Let me show you what evidence is behind this recommendation."

---

### Step 3 — The evidence (2 minutes)

**What to show:** `out/evidence-ledger.json` — show both entries

```json
[
  {
    "evidence_id": "ev-...",
    "hash": "a3f2...",
    "source_type": "edr_alert",
    "ingested_at": "2026-05-01T10:05:00Z"
  },
  {
    "evidence_id": "ev-...",
    "hash": "7c91...",
    "source_type": "process_event",
    "ingested_at": "2026-05-01T10:05:00Z"
  }
]
```

**Narration:**

> "Two evidence entries. The EDR alert itself, and the process event — the PowerShell
> execution with the encoded command.
>
> Each entry has a SHA-256 hash of its exact content. Not a summary. Not a
> description. The hash of the canonical bytes of the original object.
>
> This matters because later, when we replay, we recompute these hashes from the
> stored content and compare them. If anything was tampered with — if a single byte
> changed — the replay fails and tells you exactly which evidence entry was affected.
>
> The evidence is locked in at ingestion time. It cannot be quietly edited after the
> fact."

**Point to the `evidence_refs` in the action card:**

> "And notice — the action card's `evidence_refs` field lists these exact evidence
> IDs. The recommendation is not floating free. It is anchored to specific,
> hash-verified evidence."

---

### Step 4 — The deterministic verdict (1.5 minutes)

**What to show:** `out/verdict.json`

```json
{
  "value": "confirmed_malicious",
  "evidence_refs": ["ev-...", "ev-..."],
  "model_contribution": false,
  "signing_tag": "sig-...",
  "set_at": "2026-05-01T10:05:01Z"
}
```

**Narration:**

> "The verdict is `confirmed_malicious`. It was derived from the two evidence
> entries — the EDR alert triggered a medium-severity finding, the process event
> triggered a high-severity finding. High severity maps to `confirmed_malicious`.
>
> `model_contribution` is false. This verdict was produced by a deterministic rule
> set, not by an AI model. Same input, same verdict, every time. You can run this
> pipeline a hundred times on the same alert and get the same result.
>
> The `signing_tag` is a SHA-256 hash of the exact tape state at the moment the
> verdict was set — the evidence, the findings, the verdict value. It is the
> integrity anchor. If the evidence or findings were changed after the verdict was
> set, the tag would not match.
>
> This is what 'deterministic' means in practice: the verdict is a pure function of
> the recorded inputs. No randomness. No model drift. No 'the AI felt differently
> today.'"

---

### Step 5 — The approval mode (1 minute)

**What to show:** back to `out/edr-handoff.json`, scroll to the authorization block

```json
{
  "approval_mode": "approval_required",
  "authorization_record_ref": "vault://placeholder/bootstrap",
  "execution_result": {
    "status": "pending",
    "reason": "recommendation_only_no_dispatcher_in_slice_001"
  }
}
```

**Narration:**

> "The approval mode is `approval_required`. This is not a setting that can be
> quietly changed to `autonomous` — it is a field on the action card that is set at
> creation and does not change after dispatch.
>
> The authorization record reference is a placeholder in this demo — in production
> it points to a vault record that binds the action, the tenant, the target, the
> policy version, and the human approval. Nothing dispatches until that record
> exists and is verified.
>
> Status is `pending`. The action card is a recommendation. It is waiting for a
> human. No host has been isolated."

---

### Step 6 — The reversibility and recovery plan (1.5 minutes)

**What to show:** `out/edr-handoff.json`, scroll to `rollback_plan`

```json
{
  "rollback_plan": {
    "reversibility_class": "reversible_by_edr",
    "vendor_reversal_action": "release_isolation",
    "vendor_reversal_target": {
      "kind": "host",
      "identifier": "workstation-42.corp.example"
    },
    "manual_steps": [],
    "reversal_window": "PT4H"
  }
}
```

**Narration:**

> "Before your analyst approves this action, they can see exactly what happens if
> it turns out to be a false positive.
>
> `reversibility_class` is `reversible_by_edr`. That means the EDR vendor exposes a
> reversal API. The reversal action is `release_isolation`. The reversal target is
> the same host. The reversal window is four hours — that is how long after dispatch
> the reversal is operationally reasonable.
>
> There are no manual steps. This is the best case: approve, and if you're wrong,
> one API call undoes it.
>
> Compare that to `disable_account`, where `reversibility_class` would be
> `manual_recovery_required` — the analyst would see the manual steps listed before
> they approve. Or a file deletion, which would be
> `irreversible_requires_compensation` — the analyst would know before clicking that
> this cannot be undone.
>
> The reversal plan is not an afterthought. It is part of the action card. It is
> surfaced at approval time, not discovered after the fact."

---

### Step 7 — Run the replay (30 seconds)

**What to show:** terminal

```bash
# The replay already ran as part of the pipeline.
# Show the output line from the original run:
# Replay: succeeded
```

**Narration:**

> "The replay ran automatically as part of the pipeline. Let me show you what it
> verified."

---

### Step 8 — Evidence hashes verified (1 minute)

**What to show:** `out/replay-report.json`, scroll to the payload

```json
{
  "replay_state": {
    "mode": "recorded_output",
    "state": "succeeded"
  },
  "audit_chain_entry": {
    "event_type": "tape_replayed",
    "payload": {
      "evidence_hashes_verified": true,
      "verdict_recomputed": "confirmed_malicious",
      "verdict_matched": true
    }
  }
}
```

**Narration:**

> "The replay verified two things.
>
> First: `evidence_hashes_verified: true`. The replay recomputed the SHA-256 hash
> of every evidence entry from the stored content and compared it against the
> recorded hash. They matched. The evidence was not tampered with between ingestion
> and replay.
>
> If a single byte had changed — if someone had quietly edited the process event
> after the fact — this would be `false` and the replay state would be `failed` with
> reason `evidence_corruption`, naming the specific evidence ID that failed."

---

### Step 9 — Verdict recomputed (1 minute)

**Narration (continuing from Step 8):**

> "Second: `verdict_recomputed: confirmed_malicious`, `verdict_matched: true`. The
> replay ran the same rule set against the recorded evidence and got the same
> verdict.
>
> The replay mode is `recorded_output`. That means it made no live network calls,
> invoked no model, and read no external state. Everything it needed was in the
> recorded tape. The proof package is self-contained.
>
> An auditor six months from now can take this file, the investigation tape, and the
> rule set, and verify independently that the verdict was correct given the evidence
> at the time. They do not need access to Zovark's infrastructure. They do not need
> the original AI model. The proof stands on its own."

---

### Step 10 — The proof report (1 minute)

**What to show:** `out/customer-report.md` — open in a readable viewer, show the
top section

```markdown
# Zovark Proof Package

Zovark is the audit-grade evidence layer for AI-assisted SOC response.

---

## Recommended Action (EDR Action Card)

**Action:** ISOLATE_HOST
**Target:** workstation-42.corp.example (host)
**Approval required:** YES — no action has been dispatched
**Evidence basis:** ev-..., ev-... (2 evidence items)
**Verdict:** CONFIRMED_MALICIOUS
**Reversibility:** reversible_by_edr — automatic release_isolation available
**Authorization:** vault://placeholder/bootstrap (bootstrap mode)

> No action has been dispatched. Human approval is required before any EDR action.

---

## Replay Proof

**Replay result:** succeeded
**Evidence hashes verified:** yes
**Verdict recomputed:** CONFIRMED_MALICIOUS (matches recorded verdict)
```

**Narration:**

> "This is the proof report. It is the artifact your analyst reads before approving,
> and the artifact your client or auditor reads after.
>
> It opens with the action card — the recommended action, the target, the approval
> status, the evidence basis, the verdict, the reversibility class. Everything the
> analyst needs to make an informed decision, in one place, before they click
> anything.
>
> Immediately below that is the replay proof — the verification that the evidence
> was not tampered with and the verdict was correctly derived.
>
> The internal mechanics — the tape ID, the audit chain entries — are at the bottom.
> They are there for the auditor. They are not the first thing the analyst sees.
>
> This is what 'showing your work' looks like for AI-assisted SOC response."

---

## Closing (1 minute)

**Narration:**

> "One command. No credentials. No network. No AI model running during replay.
>
> The architecture is designed for live EDR feeds, vault-backed authorization, and
> multi-tenant MSSP deployment. This demo runs on a static sample to show the
> structure of the proof package without any live dependencies.
>
> What we are looking for is design partners — MSSP or enterprise SOC teams who will
> review this action card format and proof package structure with us. You tell us
> whether this matches your approval workflow and your compliance requirements. We
> incorporate your feedback before we build the live EDR integration.
>
> Does this solve a real problem for your team?"

---

## Handling questions

**"Does this require an AI model?"**

> "No. This demo is fully rule-driven — the findings and verdict come from a static
> rule set, not a model. The architecture supports model-contributed findings in
> later versions, but the proof package and replay work identically whether or not a
> model was involved. The point is that whatever produced the recommendation, the
> evidence is recorded and the verdict is replayable."

**"What EDR vendors do you support?"**

> "The architecture is vendor-agnostic. This demo uses a static sample. Live EDR
> integration is the next milestone after design-partner feedback. We are designing
> the adapter interface to support CrowdStrike, SentinelOne, and Microsoft Defender
> first."

**"What does 'approval required' mean in production?"**

> "In production, the action card is presented to an analyst in your approval
> workflow. The analyst reviews the evidence, the verdict, and the reversal plan,
> then records their approval in the authorization record. The EDR adapter does not
> dispatch until that record exists and is verified. Autonomous mode — where the
> system dispatches without per-action human approval — is a future capability that
> we have explicitly deferred. Every action in the current product requires human
> approval."

**"What happens if the replay fails?"**

> "If any evidence hash does not match, the replay state is `failed` with reason
> `evidence_corruption` and the specific evidence ID is named. If the verdict
> recomputation produces a different result, the state is `mismatch` and the
> differing fields are listed. Both outcomes are recorded in the audit chain. A
> failed replay is itself evidence — it tells you that something changed between
> ingestion and replay, and it tells you exactly what."

**"Can I see the investigation tape?"**

> "Yes — `investigation-tape.json`. It is the internal proof substrate: the
> immutable record that contains the evidence ledger, timeline, findings, verdict,
> and action card reference. The action card and proof package are derived from it.
> The tape is what makes replay possible — it records every input that contributed
> to the verdict so the replay engine can reconstruct the reasoning without any live
> dependencies."

**"How does this fit into our existing SIEM or ticketing workflow?"**

> "The proof package is a set of JSON files and a Markdown report. In the current
> version you receive the bundle as output. Integration with your ticketing system,
> SIEM, or approval workflow is part of the design-partner conversation — we want to
> understand your workflow before we build the integration layer."

---

## Demo timing guide

| Step | Content | Time |
|---|---|---|
| Setup | Files open, output ready | pre-call |
| 1 | Noisy EDR sample | 1 min |
| 2 | EDR action card | 2 min |
| 3 | Evidence | 2 min |
| 4 | Deterministic verdict | 1.5 min |
| 5 | Approval mode | 1 min |
| 6 | Reversibility/recovery plan | 1.5 min |
| 7 | Run replay | 0.5 min |
| 8 | Evidence hashes verified | 1 min |
| 9 | Verdict recomputed | 1 min |
| 10 | Proof report | 1 min |
| Close | Ask | 1 min |
| **Total** | | **~14 min** |

Cut Steps 7–9 to a single 1-minute block if time is short. The replay section can
be summarised as: "The replay verified the evidence hashes and recomputed the
verdict. Both matched. The proof is self-contained and verifiable offline."
