# Zovark Proof Package

**Zovark is the audit-grade evidence layer for AI-assisted SOC response.**

---

## Recommended Action (EDR Action Card)

**Action:** ISOLATE_HOST
**Target:** HOST-12 (HOST-12.corp.example)
**Approval required:** YES — no action has been dispatched
**Evidence basis:** 5 evidence items (see below)
**Verdict:** CONFIRMED_MALICIOUS
**Reversibility:** reversible_by_edr — automatic `release_isolation` available
**Authorization:** vault://placeholder/bootstrap (bootstrap mode)

> No action has been dispatched. Human approval is required before any EDR action is taken.

---

## 1. What happened?

At 09:14 UTC on 2026-05-02, a user on HOST-12 opened a document that caused
Microsoft Word (`winword.exe`) to spawn a hidden PowerShell process with an
encoded command. The PowerShell process then:

1. Connected to an external IP (192.168.1.100) over HTTPS and downloaded 96 KB.
2. Attempted to read LSASS memory — a credential dumping technique (T1003.001).
3. Attempted to move laterally to HOST-13 via SMB (blocked by firewall).

The sequence is consistent with a phishing-delivered implant executing a
multi-stage attack: initial access → C2 communication → credential theft →
lateral movement.

---

## 2. What evidence supports it?

| # | Evidence ID | Type | Timestamp | Key detail |
|---|---|---|---|---|
| 1 | ev-d7b730986af5a14c5...3eb | edr_alert | 09:14:00Z | winword.exe spawned powershell.exe |
| 2 | ev-7c755e0085c136525...d01 | process_event | 09:14:03Z | powershell.exe -EncodedCommand (hidden window) |
| 3 | ev-8f2999eb2acbf1ac4...f9 | network_event | 09:14:07Z | 192.168.1.100:443, 98 KB received |
| 4 | ev-b6d04ab6ccf177c7d...3c | credential_access | 09:14:11Z | LSASS memory read (T1003.001) |
| 5 | ev-a4791665e335c3170...b5 | lateral_movement_attempt | 09:14:19Z | SMB to HOST-13 (blocked) |

Each evidence entry carries a SHA-256 hash of its exact content. The hashes are
verified during replay — any post-ingestion tampering would cause replay to fail
with `evidence_corruption`.

---

## 3. Why was this verdict reached?

**Verdict:** `confirmed_malicious`

**Derivation rule:** Any finding with severity `critical` or `high` → `confirmed_malicious`

**Findings that triggered this verdict:**

| Finding | Severity | MITRE |
|---|---|---|
| Office application spawned encoded PowerShell | high | T1059.001 |
| PowerShell contacted external IP over HTTPS | high | T1071.001 |
| Credential access via LSASS memory read | **critical** | T1003.001 |
| Lateral movement attempt to HOST-13 (blocked) | high | T1021.002 |

The verdict is **deterministic** — it is a pure function of the recorded findings.
No AI model contributed. Same evidence, same rules, same verdict every time.

`model_contribution: false` on all findings and on the verdict.

---

## 4. What response action is recommended?

**Isolate HOST-12.**

Rationale: The host has demonstrated active C2 communication, credential dumping,
and lateral movement intent. Isolation stops the active threat while preserving
forensic state for investigation.

The action card (`edr-handoff.json`) contains the full structured recommendation
including evidence links, policy snapshot, and rollback plan.

---

## 5. What is the approval mode?

**approval_required**

No action has been dispatched. The action card is a recommendation. A human
approver must review this proof package and record their approval before any
EDR action is taken.

Authorization record: `vault://placeholder/bootstrap` (bootstrap mode — production
vault runtime is a future milestone).

---

## 6. What is the blast radius?

**Directly affected:** HOST-12 only.

- All active user sessions on HOST-12 will be terminated.
- All processes on HOST-12 will lose network access.
- Shared drives mounted from HOST-12 will become unavailable.

**Lateral movement:** HOST-13 was targeted but the attempt was blocked by the
firewall before isolation. No other hosts are known to be compromised.

**User impact:** CORP\jsmith is the active user on HOST-12. Credential rotation
for this account is recommended regardless of isolation outcome, given the LSASS
access event.

---

## 7. How can the action be reversed or recovered?

**Reversibility class:** `reversible_by_edr`

If isolation is approved and later found to be a false positive:

- The EDR vendor API can release isolation automatically (`release_isolation`).
- No manual OS-level steps are required.
- Reversal window: 4 hours from dispatch.

**Regardless of isolation outcome:**
- Rotate credentials for CORP\jsmith (LSASS was accessed; assume credentials compromised).
- Review the downloaded payload at `C:\Temp\svchost.exe` (decoded from the PowerShell command).
- Investigate the C2 IP 192.168.1.100.

---

## 8. Can the decision be replayed?

**Yes. Replay result: succeeded.**

The replay engine verified:

| Check | Result |
|---|---|
| Evidence hashes verified | ✅ all 5 entries matched |
| Verdict recomputed | ✅ `confirmed_malicious` |
| Verdict matched stored verdict | ✅ |
| Live LLM call during replay | ❌ none |
| Live EDR call during replay | ❌ none |

The proof package is self-contained. An auditor can verify the reasoning offline,
months or years later, without access to Zovark's infrastructure or the original
EDR system.

Replay ID: `replay-001`
Replay mode: `recorded_output`

---

## Audit Chain

| Entry | Event | Entry ID | Hash |
|---|---|---|---|
| 1 | tape_recording_closed | audit-entry-1 | 5cfefb79ab9b421b...35a5 |
| 2 | tape_replayed | audit-entry-2 | 45070e44a4eee12d...4be3 |

Chain: hash-linked. Entry 2's `prev_entry_hash` equals entry 1's `this_entry_hash`.
Root signing deferred to M1+ (production vault runtime).

---

## Internal Proof Substrate

Tape ID: tape-001
Tenant: tenant-demo
Source alert: alert-20260502-001
Generated: 2026-05-02T09:14:22Z
Schema: tape/1.0
Signing tag: sig-772cf462adf840cfe311e2b5606e74fa49995b5b3d690c2cd4a78d3db1548df2

---

## Artifacts

- `edr-handoff.json`          ← EDR action card (hero artifact)
- `replay-report.json`        ← Replayable proof package (hero artifact)
- `customer-report.md`        ← This document
- `investigation-tape.json`   ← Internal proof substrate
- `evidence-ledger.json`
- `timeline.json`
- `findings.json`
- `verdict.json`
