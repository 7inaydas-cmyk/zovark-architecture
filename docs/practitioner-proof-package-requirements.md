# Practitioner Proof Package Requirements

Status: docs-only requirements note for Proof Package V2. This document does not
change runtime code, proof-package schema, verifier behavior, V3 adapter behavior,
or generated package output.

## Purpose

Proof Package V1 remains the current nine-file deterministic package. It proves
that exported Slice proof artifacts are internally consistent and replay-verifiable
offline.

Proof Package V2 is a future versioned extension intended to make the proof package
more useful to SOC, incident-response, MDR, and audit-adjacent practitioners after
V2 architecture and realistic scenario validation are complete. This document
captures the practitioner-facing information classes that a V2 package should be
able to represent without turning them into current product claims.

## Evidence Boundary

Inputs used for this requirements note:

- current final architecture synthesis
- Capability Identity Contract
- Investigation Trace V1 spec
- V3 fixture capture report
- V3 asset inventory and V3-to-v4 domain map
- current V3 adapter and generated-package verification tests
- practitioner-oriented requirement categories supplied for Proof Package V2

This document does not claim validated customer demand. The final architecture
synthesis currently says no validated customer signals have been captured yet.
Customer outreach should not start from V2 claims until the V2 architecture is
implemented and tested on realistic scenarios.

## Core Compatibility Requirements

- Proof Package V1 remains the current nine-file deterministic package.
- Proof Package V2 is a versioned extension, not a silent mutation of V1.
- Replay must continue verifying V1.
- V2 verifier support must be implemented in a later PR before V2 is presented as
  verified behavior.
- V2 must preserve deterministic verification.
- Any value not populated from V3 or deterministic proof synthesis must be `null`
  plus `data_unavailable_reason`.
- V2 must not require replay to call live EDR, SIEM, LLM, DB, network,
  dispatcher, Vault runtime, or external systems.

## Practitioner Requirement Classes

| Requirement class | Why practitioners need it | V2 object | Initial classification |
| --- | --- | --- | --- |
| Why Zovark reached the decision | Analysts need an evidence-tied explanation, not just a verdict. | `decision_rationale` | required |
| Why this was not treated as benign noise | Analysts need explicit false-positive reasoning where available. | `false_positive_reasoning` | conditional |
| What context shaped the investigation | MDR/SOC teams need enrichment provenance and context boundaries. | `context_enrichment` | conditional |
| What Zovark could not see | Reviewers need gaps and assumptions before trusting a package. | `visibility_gaps` | required |
| Who approved or reviewed the action | High-stakes response needs approval path evidence. | `approval_record` | required |
| What could be impacted | Response leads need scoped blast-radius reasoning. | `blast_radius` | conditional |
| How to undo or contain response safely | Incident commanders need rollback or recovery notes when action is proposed. | `rollback_plan` | conditional |
| Which frameworks the evidence maps to | Compliance teams need bounded mappings, not certifications. | `compliance_mapping` | optional |
| Which controls were in place at incident time | Reviewers need to know the relevant control context. | `controls_in_place_at_incident` | customer-supplied |
| Customer-readable explanation of V2 proof | Design partners need a bounded readable summary. | `customer_report_v2` | required |

## Required Safety Rules

- Do not expose raw model chain-of-thought.
- Use structured decision rationale summaries tied to evidence IDs.
- Do not expose raw system prompts by default.
- Prefer `prompt_hash`, `prompt_version`, `model_ref`, `model_fingerprint`, and
  redacted prompt references.
- Do not implement signing or external anchoring in this contract.
- Do not claim legal admissibility.
- Do not claim compliance certification.
- Compliance mappings must be versioned and labeled as mappings, not
  certifications.
- If V3 does not emit a value, represent absence with `null` plus
  `data_unavailable_reason`.
- Preserve deterministic verification.
- Preserve V1 compatibility.

## V3 Data Readiness

| Data area | Current readiness | Boundary |
| --- | --- | --- |
| V3 execution path distinction | Partially represented by current adapter context. | V2 should preserve deterministic tools, LLM-selected tools, sandbox fallback, and explicit sandbox mode when available. |
| Model invocation identity | Specified by Capability Identity and Trace docs, but not emitted as first-class objects by the current adapter. | V2 must not imply live model replay. |
| Prompt identity | Hash/version fields are expected where available. | Raw system prompts should not be exported by default. |
| Generated code and sandbox evidence | Preserved only when fixture data includes hashes/results. | Missing values require `data_unavailable_reason`. |
| Governance decisions | V3 evidence exists, but it does not replace Vault authorization. | Approval and governance must remain distinct. |
| Context lookups | Institutional and correlation lookup evidence exists in older runtime assets. | V2 must distinguish recorded context from live lookup. |
| Customer control state | Not reliably emitted by V3. | Treat as customer-supplied until runtime evidence exists. |

## Customer-Discovery Boundary

Before customer outreach uses Proof Package V2 language:

1. V2 architecture must be implemented in docs and code according to this contract.
2. Static V2 fixtures must validate.
3. A V2 verifier skeleton must exist and fail closed.
4. V3 adapter population must be tested on realistic scenarios.
5. AlertForge or equivalent realistic scenario validation must pass.
6. The customer-readiness package must clearly label V1 current behavior versus V2
   planned or implemented behavior.
