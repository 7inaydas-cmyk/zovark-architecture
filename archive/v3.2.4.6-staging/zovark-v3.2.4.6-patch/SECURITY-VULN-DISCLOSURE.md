# Zovark Security Vulnerability Disclosure Policy

**Owners:** security-officer, ops.
**Established by:** ADR-0040 §11 + ADR-0042 compromise response.
**Effective from:** v3.2.4.2 (M1-DOC-005).
**Implementation status:** Policy document. `ops/security/vuln-ledger.jsonl` and `scripts/check_vuln_ledger_chain.py` are M2 deliverables and are not present in this patch tree.

## 1. Scope

This document governs how Zovark handles security vulnerabilities discovered:
- By the Research Pipeline during nightly code-audit runs
- By external security researchers
- By customers
- By Zovark engineers in the course of normal work

It also governs cryptographic key compromise events per ADR-0042.

## 2. Reporting a vulnerability

If you have discovered a vulnerability in Zovark, please email **security@zovark.io**. PGP-encrypted reports are preferred:

```
Fingerprint:  <to be generated at M2 alongside HSM bring-up>
Public key:   https://zovark.io/.well-known/security.asc
```

We acknowledge receipt within **2 business days** `[policy-commitment:security-officer,quarterly-review]`. We provide a triage decision within **5 business days** `[policy-commitment:security-officer,quarterly-review]`.

## 3. Embargo queue (mandatory for findings of CVSS >= 4.0 `[policy-commitment:security-officer,quarterly-review]`)

When a finding is classified as a security vulnerability (CVSS >= 4.0 `[policy-commitment:security-officer,quarterly-review]`, or any of: RCE, auth bypass, tenant boundary violation, audit chain mutation, key compromise, signing bypass), it does **NOT** enter the public PR queue. Instead:

1. Finding is written to future `ops/security/vuln-ledger.jsonl` (append-only, hash-chained). This ledger is an M2 deliverable.
2. Real-time notification to the security-officer.
3. Embargo timer starts (per §4 below).
4. Patch is developed in a private branch (Tier 3 review per ADR-0040).
5. Patch is built into a release bundle (per ADR-0039 two-key signing).
6. Customer notification is sent **7 days before public disclosure** `[policy-commitment:security-officer,per-advisory-review]`.
7. Public disclosure: GitHub Security Advisory + CVE coordination if applicable + blog post.

## 4. Embargo timers

| Severity | CVSS range | Default embargo | Maximum embargo |
|---|---|---|---|
| Low | 0.1-3.9 `[policy-commitment:security-officer,quarterly-review]` | 14 days `[policy-commitment:security-officer,quarterly-review]` | 30 days `[policy-commitment:security-officer,quarterly-review]` |
| Medium | 4.0-6.9 `[policy-commitment:security-officer,quarterly-review]` | 30 days `[policy-commitment:security-officer,quarterly-review]` | 60 days `[policy-commitment:security-officer,quarterly-review]` |
| High | 7.0-8.9 `[policy-commitment:security-officer,quarterly-review]` | 30 days `[policy-commitment:security-officer,quarterly-review]` | 60 days `[policy-commitment:security-officer,quarterly-review]` |
| Critical | 9.0-10.0 `[policy-commitment:security-officer,quarterly-review]` | 14 days `[policy-commitment:security-officer,quarterly-review]` | 30 days `[policy-commitment:security-officer,quarterly-review]` |

Critical embargo is shorter because customer exposure is higher; urgency-to-ship overcomes the polish window.

## 5. What is NOT a security vulnerability for embargo purposes

These findings go to the **public PR queue**, not the embargo queue:

- Dead code findings
- Schema drift findings (compatibility, not security)
- Performance regressions
- Test flakiness
- Documentation errors
- Missing translations
- Style / lint violations

The embargo queue is for vulnerabilities that, if disclosed before patched, would let an attacker compromise a customer instance.

## 6. Vuln-ledger format

Future `ops/security/vuln-ledger.jsonl` — one JSON object per line, append-only, hash-chained. This file is an M2 deliverable and is not present in this patch tree.

```jsonl
{"vuln_id":"ZVK-VULN-0001","discovered_at":"<timestamp>","discovered_by":"<source>","severity":"high","cvss":"<score>","affected_versions":["<range>"],"embargo_until":"<timestamp>","status":"under_embargo","prev_hash":"<sha256>","entry_hash":"<sha256>"}
{"vuln_id":"ZVK-VULN-0001","action":"patch_developed","at":"<timestamp>","status":"patch_in_review","prev_hash":"<sha256>","entry_hash":"<sha256>"}
{"vuln_id":"ZVK-VULN-0001","action":"customer_notified","at":"<timestamp>","status":"customer_notified","prev_hash":"<sha256>","entry_hash":"<sha256>"}
{"vuln_id":"ZVK-VULN-0001","action":"public_disclosure","at":"<timestamp>","status":"public","cve_id":"<CVE-ID>","prev_hash":"<sha256>","entry_hash":"<sha256>"}
```

The ledger must be reproducible from a clean clone after embargo lifts and entries become public. Hash-chain integrity verification by `scripts/check_vuln_ledger_chain.py` is an M2 deliverable.

## 7. Customer notification template

Email subject: `[Zovark Security Advisory] <SEVERITY>: <SHORT-TITLE>`

```
Dear Zovark customer,

We are writing to inform you of a security vulnerability affecting
Zovark versions <range>. A patched bundle is available now:

  Bundle ID:        <bundle-id>
  Bundle version:   <version>
  Verification:     zovark update verify <bundle-path>

CVE ID (if applicable):  <CVE-ID>
Severity:                <Low/Medium/High/Critical> (CVSS <score>)
Discovery date:          <date>
Public disclosure date:  <date> (7-day customer notice per §3)

Vulnerability summary:
  <one-paragraph description of the issue and its impact>

Affected versions:
  <semver range>

Required action:
  Apply the patched bundle within <window> using your usual update flow.
  For air-gap deployments, the offline package is available at:
    <air-gap-package-uri>

We are not aware of any active exploitation of this vulnerability.
If you have questions or need assistance, please contact:
  security@zovark.io

— Zovark Security Team
```

## 8. Cryptographic key compromise (per ADR-0042)

If a release-engineer or security-officer key is suspected compromised:

1. **Immediate revocation:** affected key revoked at HSM within 1 hour of suspicion `[policy-commitment:security-officer,incident-review]`.
2. **Root attestation of revocation:** Root quorum signs a `key_revocation_event` into the future `key-ledger.jsonl`.
3. **Replacement key generation:** new key generated under same HSM ceremony procedure.
4. **Transition signing:** during a 30-day transition window `[policy-commitment:security-officer,incident-review]`, release bundles are signed by the uncompromised counterpart role key plus the new replacement key, with Root-attested revocation metadata. The compromised key is never used again.
5. **Customer-verification key update:** customer-verification public keys updated via signed bundle (chained from existing customer-verification key).
6. **Old key retired:** after 30-day transition `[policy-commitment:security-officer,incident-review]`, old key remains permanently revoked.
7. **Public disclosure:** after transition complete, full incident report published per §3 above.

If the **Root of Trust** is compromised (which would require at least 3 of 5 key-share holders to be compromised simultaneously `[policy-commitment:security-officer,annual-review]`), we initiate a coordinated re-issuance under a new Root ceremony, with customer notification 30 days before old-Root retirement `[policy-commitment:security-officer,incident-review]`. This is the worst-case event and has no automated path; it is an operational drill rehearsed twice per year `[policy-commitment:security-officer,semiannual-review]`.

## 9. Researcher acknowledgements

External security researchers who responsibly disclose vulnerabilities are acknowledged in the public advisory (with their consent) and listed at https://zovark.io/security/researchers. We do not currently operate a paid bug bounty. `[policy-commitment:security-officer,annual-review]`

## 10. Audit

This document and the future `vuln-ledger.jsonl` are protected under OWNERS.yaml as Tier 3. Any modification requires 2 maintainer reviewers + security-officer + 7-day review window `[policy-commitment:security-officer,per-change-review]`.
