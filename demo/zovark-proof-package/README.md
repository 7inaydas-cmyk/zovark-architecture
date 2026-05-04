# Zovark — Demo Proof Package

> **This is a static demo artifact package for the YC application.**
> It shows the intended first proof-package output shape.
> The full pipeline implementation is in progress.

---

## What this is

This package demonstrates what Zovark produces for a single high-risk SOC decision:
**should we isolate HOST-12?**

It contains a realistic EDR alert scenario and the complete proof package that
Zovark generates before any action is approved — evidence ledger, timeline,
findings, deterministic verdict, approval-required action card, and a replayable
proof bundle.

**Nothing in this package is live.** No EDR API was called. No AI model ran. No
network requests were made. The hashes are real SHA-256 values computed from the
evidence objects. The audit chain entries are hash-linked. The replay verification
claims are accurate.

---

## Scenario

A user on HOST-12 opens a phishing document. Microsoft Word spawns a hidden
PowerShell process with an encoded command. The PowerShell process contacts an
external IP, reads LSASS memory (credential dumping), and attempts lateral movement
to HOST-13 (blocked by firewall).

**Core question:** Should the SOC approve host isolation?

---

## Package structure

```
samples/
  edr/
    phishing-powershell.json    ← Raw EDR alert input

out/
  tape-001/
    customer-report.md          ← Human-readable proof report (start here)
    edr-handoff.json            ← Approval-required EDR action card
    replay-report.json          ← Replayable proof package
    investigation-tape.json     ← Internal proof substrate
    evidence-ledger.json        ← 5 evidence entries with SHA-256 hashes
    timeline.json               ← 13 timeline events
    findings.json               ← 4 rule-driven findings
    verdict.json                ← Deterministic verdict

demo-script.md                  ← 90-second screen recording script
README.md                       ← This file
```

---

## How to read this package

**Start with `out/tape-001/customer-report.md`.**

It answers eight questions in order:
1. What happened?
2. What evidence supports it?
3. Why was this verdict reached?
4. What response action is recommended?
5. What is the approval mode?
6. What is the blast radius?
7. How can the action be reversed or recovered?
8. Can the decision be replayed?

Then open `edr-handoff.json` to see the structured action card, and
`replay-report.json` to see the verification result.

---

## What makes this different from a SIEM alert

A SIEM alert tells you something happened. This proof package tells you:

- **What evidence** justified the recommendation (with content hashes).
- **Why the verdict** was reached (deterministic rule, no AI black box).
- **Who must approve** before anything is dispatched (approval_required gate).
- **What the blast radius is** before you click approve.
- **How to reverse it** if it turns out to be a false positive.
- **That the reasoning can be replayed** by any auditor, offline, months later.

---

## Implementation status

| Component | Status |
|---|---|
| Architecture spec (rc3) | ✅ frozen |
| Slice 001 Kiro spec | ✅ complete |
| canonical.py + hashing.py | ✅ implemented, 51/51 tests passing |
| ingest.py (Task 3) | 🔄 in progress (Claude Code) |
| tape.py, findings.py, verdict.py | ⏳ pending |
| handoff.py, audit.py, replay.py | ⏳ pending |
| writer.py + CLI | ⏳ pending |
| Live EDR integration | ⏳ post-Slice 001 |
| Production vault runtime | ⏳ M3 |

The demo artifacts in this package were hand-crafted to show the intended output
shape. The pipeline that generates them automatically is being built task by task.

---

## Hard constraints (permanent)

- No live EDR API calls.
- No autonomous action dispatch.
- No Sigma rule generation.
- No SIEM publication.
- No production credential vault.
- No live LLM calls.
- No network calls.
- `approval_mode: approval_required` always.
- `execution_result.status: pending` until a human approves.
