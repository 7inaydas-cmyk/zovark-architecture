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

demo-recording.html             ← 7-scene founder walkthrough (record with Loom)
demo.html                       ← Full static HTML reference
demo-script.md                  ← 90-second screen recording script
README.md                       ← This file
```

---

## Validation

All JSON artifacts in this package were validated before commit. Evidence hashes
and audit-chain links were computed deterministically for this static walkthrough.

To regenerate or re-validate (requires Python 3.11+, no other dependencies):

```bash
python scripts/generate_yc_demo.py
python scripts/validate_yc_demo.py
```

Both scripts live in `scripts/` at the repo root.

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
