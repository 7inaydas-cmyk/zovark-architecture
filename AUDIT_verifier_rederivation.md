# Audit — verifier full-chain re-derivation fix

A FRESH independent adversarial auditor was given only the diff (`main..HEAD`) and the
design note, and tasked to find any path where a tampered/unfaithful package verifies
clean, plus any new defect. **Result: zero unresolved dangerous-direction findings.**

## Confirmed correct

- **Hole closed (v1 AND v2).** `_validate_derived_chain` re-derives findings from
  `raw_evidence` and the verdict from those findings, rejecting any divergence. It is
  called from `_reconstruct_verified_tape`, the single chokepoint both the v1 and the
  v2 (`_validate_loaded_v2_package → _verify_v1_package`) paths flow through. Evidence
  `hash == sha256(raw_content)` and `evidence_id` are independently re-checked during
  replay re-derivation, so findings are derived from hash-bound bytes.
- **Accept-valid preserved.** The real slice001 package still verifies (exit 0, same
  summary: 7 checks, `confirmed_malicious`). slice001 OUTPUT byte-identical
  (`8749bf8a…3445a0`); the diff touches only the verifier, its tests, and the design
  note — 0 lines in any generation module.
- **Suites green:** full architecture suite 510 passed; verifier suite 90 passed; all
  5 CI scripts pass.

## Attacks attempted — all rejected or accepted-only-when-legitimate

| Attack | Result |
|---|---|
| Forged benign findings over malicious evidence (v1) | REJECTED `findings_mismatch` |
| Same forgery built through the V2 path (findings+tape tampered to pass extracted-views) | REJECTED `findings_mismatch` |
| Severity / evidence-ref / verdict-field tampering | REJECTED (deterministic re-derivation) |
| `no_findings_flag` set true / non-bool | REJECTED (`findings_mismatch` / `verdict_mismatch`) |
| 819-case poison fuzz across all top-level artifact fields | 0 uncaught exceptions, 0 false-accepts (6 "accepts" were Python `==` no-ops, e.g. `0==False` — semantically identical, no integrity loss) |

## Fail-closed residuals — all clean (FAIL-SAFE)

Non-UTF-8 customer report, lone surrogate, deeply-nested JSON, `Infinity`/`NaN`,
oversized integer, >16 MiB artifact, symlinked artifact to a wrong/broken target — all
raise a clean `ZovarkValidationError` (CLI exit 3); no uncaught traceback. No
`eval`/`exec`/`subprocess`/`socket`/`pickle`/network/secret introduced.

## Classification

- DANGEROUS-DIRECTION: **none unresolved.**
- FAIL-SAFE / documented: the `bool(no_findings_flag)` coercion is harmless (a non-bool
  flag is caught downstream by `derive_verdict`'s strict bool check — confirmed
  rejected). The product consequence (notify_only/benign/low-confidence packages are
  now non-derivable and rejected; the V2 false-positive-reasoning branch is
  forward-looking) is the correct fail-safe direction, documented in
  `DESIGN_verifier_rederivation.md`, and the FP classification stays unit-pinned.
