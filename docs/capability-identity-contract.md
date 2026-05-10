# Capability Identity Contract

Status: architecture contract, docs-only. This document does not change runtime code,
proof-package schema, Replay V2 behavior, or V3 runtime behavior.

## Purpose

The Capability Identity Contract defines the minimum identity envelope required to
carry V3 runtime evidence into the proof/replay layer without losing the difference
between deterministic tools, LLM-selected tools, generated sandbox execution, and
fallback behavior.

The contract exists so future PRs can map V3 investigation output into a proof
package without replay calling live systems. It is not the Investigation Trace V1
spec. Investigation Trace V1 will define ordered events and relationships later;
this contract defines stable identities for the capabilities referenced by those
events.

## Current Implementation Status

The Capability Identity Contract is a forward-looking contract and specification.
As of the current main branch, the V3 adapter does not emit first-class Capability
Identity objects. Available V3 trace context is preserved nested inside the
existing nine-file proof package evidence substrate, which avoids a proof-package
schema bump. Implementers should not expect standalone Capability Identity
Contract objects in current generated proof packages.

This status note does not align source enum aliases, clarify `model_ref`
preservation, change Investigation Trace V1, change adapter behavior, or change
the proof-package schema. Those items remain explicitly deferred.

## Scope

This contract must support:

- V3 tools mode.
- Saved-plan deterministic path.
- LLM-selected tool path.
- V2 sandbox/codegen fallback.
- Explicit sandbox mode.
- Governance and policy decisions.
- Institutional knowledge lookup.
- Correlation history lookup.

## Non-Goals

This PR does not add:

- runtime implementation
- Capability Gateway runtime
- proof-package schema changes
- V3-to-proof adapter
- Investigation Trace V1 spec
- fixture files
- Replay V2 behavior changes
- live EDR or SIEM connectors
- manifest, provenance, signing, or transparency logs

## Required Envelope

Every proof-visible V3 capability reference must be representable with these fields.
Fields that do not apply to a capability type must be present as `null` in future
machine-readable records unless a later schema decision explicitly chooses a
different encoding.

| Field | Required Meaning |
| --- | --- |
| `capability_id` | Stable deterministic identifier for the capability instance or capability definition. |
| `capability_type` | Capability class, such as `plan`, `tool`, `model_invocation`, `sandbox_execution`, `governance_policy`, or `context_lookup`. |
| `capability_version` | Version, commit, migration, tool catalog version, prompt version, or other stable version reference. |
| `source` | One of `builtin`, `db_saved`, `llm_selected`, `template`, `generated`, or `fallback`. |
| `execution_mode` | One of `tools`, `sandbox`, or `sandbox_fallback`. Non-executing policy/context records inherit the investigation execution mode they affected. |
| `parameter_source` | One of `model`, `policy`, `human`, `template`, or `system`. |
| `input_hash` | Deterministic hash of the canonicalized capability input or `null` if no input was recorded. |
| `output_hash` | Deterministic hash of the canonicalized capability output or `null` if no output was produced. |
| `policy_ref` | Stable policy/config reference used for allow/deny/governance decisions. |
| `allow_deny_decision` | Stable policy decision such as `allow`, `deny`, `observe`, `assist`, `autonomous`, `review_required`, or `not_applicable`. |
| `model_ref` | Model identifier or pinned model reference for model-selected or model-generated work. |
| `prompt_hash` | Deterministic hash of the prompt or prompt input envelope where a model was used. |
| `prompt_version` | Stable prompt version where one exists. |
| `generated_code_hash` | Deterministic hash of generated code before scrubbing, when code generation was used. |
| `scrubbed_code_hash` | Deterministic hash of scrubbed code after safety processing, when code generation was used. |
| `ast_validation_result` | Stable AST validation result for generated or template code paths. |
| `sandbox_policy_id` | Stable sandbox policy identifier for sandbox or fallback execution. |
| `stdout_hash` | Deterministic hash of sandbox stdout where available. |
| `stderr_hash` | Deterministic hash of sandbox stderr where available. |

## Hashing Rules

Future implementation should use the existing proof/replay deterministic hashing
style where possible:

- Hash JSON-like structures only after canonical JSON serialization.
- Hash byte streams exactly as exported after deterministic normalization.
- Do not hash Python `repr()` output.
- Do not include absolute local paths, hostnames, wall-clock timestamps, random IDs,
  or environment-specific values in identity hashes.
- If a model/tool output is replayed, replay must use the recorded output and its
  hash. Replay must not call the live model, live tool, EDR, SIEM, database, or
  network.

## Capability Type Mapping

| Runtime Case | Capability Type | Source | Execution Mode | Parameter Source | Required Identity Notes |
| --- | --- | --- | --- | --- | --- |
| Saved-plan deterministic path | `plan` | `builtin` or `db_saved` | `tools` | `system` or `human` | Must identify the selected plan/template and version. |
| LLM-selected tool path | `model_invocation` and `tool` | `llm_selected` for selection, `builtin` for tool implementation | `tools` | `model` | Must record `model_ref`, `prompt_hash`, `prompt_version`, selected tool identity, and output hash. |
| V3 tool execution | `tool` | `builtin` | `tools` | `system`, `model`, `human`, `template`, or `policy` | Must hash normalized inputs and outputs and identify the tool catalog/version. |
| Tool-runner error with Path D fallback | `sandbox_execution` | `fallback` | `sandbox_fallback` | `system` or `model` | Must identify the failed tool path, fallback reason, generated/scrubbed code hashes, AST result, sandbox policy, stdout, and stderr. |
| Explicit sandbox V2 run | `sandbox_execution` | `generated` or `template` | `sandbox` | `model` or `template` | Must record code generation or template identity plus sandbox result hashes. |
| Governance decision | `governance_policy` | `builtin` or `db_saved` | inherited | `policy` | Must identify policy/config and decision. Governance does not replace Vault authorization. |
| Institutional knowledge lookup | `context_lookup` | `db_saved` | inherited | `human` or `system` | Must hash query/input and returned context if used in findings or verdict. |
| Correlation history lookup | `context_lookup` | `db_saved` | inherited | `system` | Must hash query/input and returned correlation context if used in findings or verdict. |

`inherited` means the record uses the execution mode of the investigation stage it
affected, because the required enum intentionally has no `none` value.

## Required Versus Nullable Fields

| Capability Type | Always Required | Often Nullable |
| --- | --- | --- |
| `plan` | `capability_id`, `capability_type`, `capability_version`, `source`, `execution_mode`, `parameter_source`, `input_hash`, `output_hash` | model, prompt, sandbox, stdout, stderr fields |
| `tool` | `capability_id`, `capability_type`, `capability_version`, `source`, `execution_mode`, `parameter_source`, `input_hash`, `output_hash` | generated code, sandbox, stdout, stderr fields unless the tool uses sandbox fallback |
| `model_invocation` | `model_ref`, `prompt_hash`, `prompt_version`, `input_hash`, `output_hash` | generated code and sandbox fields unless the model generated code |
| `sandbox_execution` | generated/scrubbed code hashes or template identity, `ast_validation_result`, `sandbox_policy_id`, `stdout_hash`, `stderr_hash` | model fields if the sandbox run came only from a template |
| `governance_policy` | `policy_ref`, `allow_deny_decision`, `input_hash`, `output_hash` | model and sandbox fields |
| `context_lookup` | `input_hash`, `output_hash`, `source`, `parameter_source` | model, policy, generated code, sandbox, stdout, stderr fields |

## Proof-Replay Boundary

The proof package must visibly distinguish at least these paths once V3 output is
adapted:

- deterministic tools selected by saved plan
- tools selected by model output
- sandbox/codegen fallback
- explicit sandbox execution

The current nine-file proof-package contract does not yet carry all of this as
first-class fields. A future controlled schema bump is allowed if fixture evidence
shows these distinctions cannot be represented without ambiguity. Until then, the
V3-to-proof adapter must not hide model-selected or sandbox fallback behavior behind
ordinary deterministic findings.

## Relationship To Investigation Trace V1

Capability Identity Contract records answer:

- what capability ran
- which version/source/policy/model selected it
- what inputs and outputs were hashed
- whether fallback or sandbox execution happened

Investigation Trace V1 should later answer:

- when the capability was used in the investigation sequence
- what hypothesis or finding it supported
- whether a candidate finding was accepted or rejected
- how deterministic synthesis converted runtime evidence into proof-package fields

This document intentionally stops before defining the trace schema.

## Open Constraints

- `Zovark_final` contains V3 tool execution and plan evidence, but no durable
  per-tool call record table was found in the fixture capture report.
- Full live Path C and Path D runtime outputs were not captured in PR #28.
- Customer validation has not been captured in the repo.
- The v4.1 scale target remains aspirational relative to the measured V3 evidence.
- Governance/policy records must not be treated as Vault authorization.

## Future Acceptance Gates

Before a V3-to-proof adapter can merge, it must show:

- every model-selected tool path has recorded model identity and output hashes
- every sandbox or fallback path has code, AST, sandbox policy, stdout, and stderr
  identity where available
- every proof-facing finding or verdict can be traced back to deterministic,
  model-selected, or sandbox fallback inputs without ambiguity
- Replay verification remains offline and never calls live systems
