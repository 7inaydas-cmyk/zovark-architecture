# ADR-0042 — Cryptographic Key Management

**Status:** Proposed (becomes Accepted on M1-ARCH-002 merge).
**Date:** 30 April 2026.
**Established by:** architecture extension; key-compromise transition clarified in v3.2.4.5.
**Related:** ADR-0028 (Vault threat model), ADR-0034 (DEK rotation), ADR-0039 (Update Factory).

## Review metadata

- **Scope:** M1 architecture; M4 key-management implementation for release signing.
- **Affected invariants:** INV-031.
- **Implementation status:** Document-only in this patch. No HSM integration, key ledger, rotation-age checker, compromise drill artifact, or customer-verification-key distribution exists in this tree.
- **Enforcement mechanism:** Planned M4: `check_key_quorum.py`, `check_key_rotation_age.py`, `check_revoked_keys_not_used.py`, and `key-ledger.jsonl` verifier. Until those files exist, this ADR is policy architecture only.
- **Supersession/amendment links:** Supersedes unsafe "new + old" transition wording. Not superseded.
- **Claim provenance:** Quorum, rotation, transition, and drill intervals are policy commitments.

## Context

ADR-0039 mandates two-key signing for every release bundle. This requires a real key management story: HSM choice, rotation cadence, root-of-trust ceremony, key compromise response, customer-side verification key escrow. Without this ADR, the M4 team will improvise — and improvised key management is the failure mode that makes the entire ADR-0039 supply-chain model meaningless.

## Decision

Zovark will implement cryptographic key management with the following properties.

### Key types and roles

| Key | Purpose | Storage | Rotation |
|---|---|---|---|
| `zovark-root` | Root of Trust; signs role keys | Offline HSM, ceremony-only, **3-of-5 quorum** `[policy-commitment:security-officer,annual-review]` | 5 years scheduled, or on compromise `[policy-commitment:security-officer,annual-review]` |
| `release-engineer` | Signs release bundles (one of two required) | Online HSM-backed | 12 months, or on personnel change `[policy-commitment:security-officer,quarterly-review]` |
| `security-officer` | Co-signs release bundles (the other required) | Online HSM-backed | 12 months, or on personnel change `[policy-commitment:security-officer,quarterly-review]` |
| `customer-verification` | Public key shipped with customer instance for offline bundle verification | Public; pinned at install | Updated only via signed bundle (chained) |

### HSM requirement

All private keys are HSM-backed (FIPS 140-2 Level 3 minimum). `[policy-commitment:security-officer,annual-review]` Software keys are not acceptable for any role beyond initial bootstrap.

### Quorum

Root of Trust uses **3-of-5 quorum** (any three holders can sign; all five hold their share offline; any single compromise is recoverable). Release-engineer and security-officer keys are individual but require both for any release bundle.

### Rotation cadence

- Root of Trust: 5 years scheduled, or on compromise. `[policy-commitment:security-officer,annual-review]`
- Role keys: 12 months scheduled, or on personnel change, or on compromise. `[policy-commitment:security-officer,quarterly-review]`
- DEK (per ADR-0034): per existing policy, unchanged.

### Compromise response

This section was tightened in v3.2.4.5 after a review (correctly) flagged that an earlier formulation said "new key + old key" — which is dangerous because **a compromised key is no longer trustworthy and must never re-appear in a signing chain.** The corrected procedure is:

If **one** of the two role keys (release-engineer or security-officer) is suspected compromised:

1. **Immediate revocation.** The compromised key is revoked at the HSM within 1 hour of suspicion. `[policy-commitment:security-officer,incident-review]` Its key_id is added to a revocation list distributed via the next signed bundle.
2. **Root attestation of the revocation.** The Root of Trust quorum (3-of-5) signs a `key_revocation_event` record into the `key-ledger.jsonl` ledger, declaring the compromised key dead.
3. **Replacement key generation.** A new key for the affected role is generated under the same HSM ceremony procedure. The new key is also Root-attested.
4. **Transition signing.** During the transition window (default 30 days) `[policy-commitment:security-officer,incident-review]`, every release bundle requires:
   - The **uncompromised counterpart role key** (e.g., if release-engineer was compromised, the security-officer key is the counterpart).
   - The **new replacement key** for the compromised role.
   - A **Root-attestation reference** (the key_ledger entry hash from step 2) embedded in the bundle's `attestation` block.
   - **The compromised key is never used again** — it does not co-sign during transition, even with a "new key + old key" scheme. That scheme is forbidden.
5. **Customer-verification key update.** Customer-side verification keys are updated via a signed bundle that itself uses the transition signing rule above.
6. **Old key fully retired.** After the transition window, the compromised key's revocation entry remains permanent in the ledger; the new replacement key continues as the live role key.
7. **Public disclosure.** After the transition window completes, the incident is published in `SECURITY-VULN-DISCLOSURE.md` per the standard disclosure timeline.

If **both** role keys are simultaneously compromised, or if the **Root of Trust** is compromised (which would require at least 3 of 5 key-share holders to be compromised at once `[policy-commitment:security-officer,annual-review]`), the response is a coordinated re-issuance under a new Root ceremony with 30-day customer notice before old-Root retirement `[policy-commitment:security-officer,incident-review]`. This is the worst-case event and has no automated path; it is an operational drill rehearsed twice per year `[policy-commitment:security-officer,semiannual-review]`.

### Customer-side escrow

The customer-verification public key is **pinned at initial customer instance install**. Subsequent updates rotate this key only via a bundle signed with the **current** customer-verification key (chained). If a customer loses their initial install state, recovery requires Zovark support involvement (manual re-issuance + audit log).

### Air-gap operation

All signature verification works offline. Customer-verification keys do not require connectivity. Compromise notifications can be delivered via signed bundle, signed email (PGP fallback), or out-of-band media.

## Planned enforcement (M4 deliverable)

- `check_key_quorum.py` (M4): fails if any release bundle is signed with fewer than two distinct role-key signatures, or with two signatures from the same role (the latter rule enforced at the schema level by `update_bundle_signed.schema.json` `contains/minContains/maxContains` constraints in v3.2.4.5).
- `check_key_rotation_age.py` (M4): warns if any role key has not been rotated in 11+ months. `[policy-commitment:security-officer,quarterly-review]`
- `check_revoked_keys_not_used.py` (M4): cross-references every bundle signature key_id against the revocation list in `key-ledger.jsonl` and fails if a revoked key signs.
- `key-ledger.jsonl`: append-only hash-chained ledger of every key event (creation, rotation, retirement, revocation, compromise).

## Consequences

- Operational overhead: HSM procurement, ceremony procedures, rotation calendar, compromise drill twice a year. `[policy-commitment:security-officer,semiannual-review]`
- Customer trust improvement: regulated buyers' security questionnaires almost always ask about key management; this ADR is the answer.
- Onboarding friction: customer instances pin their initial verification key, which creates a "first install matters" property that must be communicated.
- Compromise response is more operationally complex than "sign with new+old during transition" but is correct: a compromised key is dead permanently.

## Alternatives considered

- *Software keys (no HSM)*: rejected; FIPS 140-2 Level 3 is table stakes for regulated buyers.
- *Single-signer with post-publish audit*: rejected; audit doesn't prevent malicious signing.
- *Sigstore Public Good only as signing service*: rejected; Sigstore Public Good logging may itself be a tenant-exposure vector. Use Sigstore Private (or self-hosted) with Public Good as a transparency log only.
- *5-of-7 Root of Trust*: rejected as operationally infeasible (loss of 3+ holders → permanent loss of root).
- *During compromise, sign with "new + old" key pair*: **explicitly rejected** in v3.2.4.5. A compromised key must not appear in any signing chain after revocation. The replacement key + uncompromised-counterpart + Root-attestation pattern preserves the two-signatures-from-distinct-roles rule without trusting the dead key.
