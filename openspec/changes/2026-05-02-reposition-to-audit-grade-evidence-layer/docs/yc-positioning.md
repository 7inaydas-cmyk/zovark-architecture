# Zovark — YC Positioning

## One line

**Zovark is the audit-grade evidence layer for AI-assisted SOC response.**

## The problem

AI is now making security recommendations — isolate this host, disable this account,
block this hash. SOC teams are acting on those recommendations. But when a regulator,
an auditor, or a customer asks "why did you isolate that machine?", the answer is
"the AI said so."

There is no evidence package. No approval record. No way to replay the reasoning.
No proof that a human reviewed it before the action was taken.

This is not a future problem. It is happening today in every SOC that has deployed
an AI-assisted detection or response tool.

## The solution

Before your SOC isolates a host or disables a user, Zovark shows the evidence,
explains the verdict, records the approval path, and creates a replayable proof
package.

Every recommended EDR action produces:

- **An approval-required action card** — the recommended action, the evidence it
  is based on, the approval gate that must be cleared before dispatch, and the
  rollback plan if the action needs to be reversed.
- **A replayable proof package** — a cryptographically-linked record that lets any
  auditor replay the investigation and verify that the verdict was correct given
  the evidence at the time.

The investigation is recorded as an immutable tape. The tape is the internal proof
substrate. The action card and proof package are what the customer sees.

## Why now

Three forces are converging:

1. **AI-assisted SOC is mainstream.** CrowdStrike, SentinelOne, and Microsoft
   Defender all have AI-driven response recommendations. The tooling exists; the
   audit layer does not.

2. **Compliance requirements are catching up.** NIS2, DORA, and emerging SEC
   guidance on AI in financial services all require documented, auditable
   decision trails for automated or AI-assisted actions. MSSPs serving regulated
   industries need this now.

3. **Liability is shifting.** When an AI-recommended action causes a business
   disruption — a false positive that isolates a production server — the question
   is no longer "did the AI make a mistake?" but "did you have a process to verify
   it before acting?" Zovark is that process.

## Traction hook

Slice 001 is runnable today:

```
python -m zovark.slice001 \
  --input samples/edr-sample-001.json \
  --output out/ \
  --tenant-id tenant-001
```

One command. One static EDR sample. No credentials. No network. Produces:
- An approval-required EDR action card
- A replayable proof package with verified evidence hashes
- A human-readable customer report

This is the demo. The architecture is frozen and evidence-backed at rc3.

## Ask

- **Design partners:** 3–5 MSSPs or enterprise SOC teams willing to review the
  Slice 001 output bundle and give feedback on the action card format and proof
  package structure.
- **YC batch:** build the production pipeline (live EDR integration, vault runtime,
  multi-tenant deployment) with design-partner feedback incorporated.
- **Pilot:** one MSSP running Zovark on real EDR alerts in approval-required mode
  by end of M3.

## What Zovark is not

- Not an EDR vendor. Zovark sits above the EDR layer and produces the evidence
  record for whatever EDR the customer already uses.
- Not an autonomous response system. Every action requires human approval in the
  current product. Autonomous mode is a future capability, explicitly deferred.
- Not a SIEM. Zovark does not aggregate logs or generate Sigma rules. It produces
  a per-investigation proof package.
- Not a compliance dashboard. The proof package is the compliance artifact; the
  dashboard is a future layer.
