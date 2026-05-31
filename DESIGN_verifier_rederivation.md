# Design note — full-chain re-derivation in `package_verifier`

Scope: a security fix to `zovark/slice001/package_verifier.py` (the authority proof-
package verifier) and its tests **only**. No ADR, schema, proof-loop, or package-
generation (slice001 output) change. slice001's output is byte-identical before and
after (combined SHA-256 of the 9 artifacts for `samples/edr-sample-001.json`:
`8749bf8af7a403110b3a622a22107cc0645e7fe8c455291da9c945e9513445a0`, unchanged).

## The defect (dangerous-direction)

The verifier re-derived the handoff/audit/replay (and, via those, the verdict) from
the recorded **findings**, and re-checked every evidence hash — but it never re-derived
the **findings from the evidence**. So a self-consistent package whose findings were
fabricated or suppressed verified clean: e.g. a genuinely malicious alert with its
findings replaced by a single `low` finding produces an internally-consistent package
at `verdict = benign` / `notify_only`, which the old verifier accepted. The findings
are the actual reasoning step that determines the verdict and the recommended EDR
action, and they were the one artifact never re-derived.

## The invariant (what changed)

`_validate_derived_chain(tape)` now re-derives the **entire chain from the recorded
evidence** and rejects any divergence:

1. `derive_findings(tape)` from `raw_evidence` must equal the recorded `findings`
   (and `no_findings_flag` must match) → else `findings_mismatch`.
2. `derive_verdict(tape)` from those findings must equal the recorded `verdict`
   → else `verdict_mismatch`.

Evidence integrity (`hash == raw_content`, `evidence_id` derivation) continues to be
re-verified independently when the replay report is re-derived. The change **only adds
rejection paths**; a package whose findings/verdict genuinely follow from its evidence
verifies exactly as before (accept-valid behavior and the verification summary are
unchanged). This ports the strict full-chain re-derivation already shipped in
`zovark-runtime`'s `proof_package/verify.py`.

## Fail-closed hardening (verifier read path)

`_load_json_file` now caps artifact size (16 MiB), rejects non-UTF-8 and non-finite
numbers (`parse_constant`), and maps `RecursionError`/oversized-int `ValueError` to
`ZovarkValidationError`. `verify_proof_package` maps any residual
`RecursionError`/`UnicodeError`/`ValueError` to a clean `ZovarkValidationError`. These
turn malformed-input crashes into clean rejections; they never turn a tampered package
into a verified one.

## Consequence for V2 / notify-only (documented, not a regression)

The deterministic rule engine (`findings.RULES`) only emits `high`/`critical`
findings, so the only **derivable** outcome today is `confirmed_malicious` /
`isolate_host`. With the invariant enforced, `notify_only`, `benign`, and
low/medium-confidence packages are **not derivable** and are now rejected
(`findings_mismatch`) — which is the correct, fail-safe direction. Consequently the V2
false-positive-reasoning branch (which gates on non-malicious verdicts) is
**forward-looking**: it cannot be exercised end-to-end until the analysis can produce
non-malicious verdicts. The V2 conditional-object enforcement itself remains covered
end-to-end by the `confirmed_malicious` demo `rollback_plan` tests; the affected
benign/notify-only tests were rewritten to assert the new (correct) rejection plus a
unit test pinning the false-positive verdict classification. This is a notable product
observation for maintainers, not a dangerous-direction issue.
