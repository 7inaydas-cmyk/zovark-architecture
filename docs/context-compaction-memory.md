# Context Compaction Memory

Status: architecture/contracts only. This document defines the Context
Compaction Memory layer for future runtime work. It does not implement runtime
memory storage, retrieval, AlertForge ingestion, benchmark harnesses, customer
readiness material, live integrations, signing, anchoring, legal evidence
packaging, or verifier behavior changes.

## Purpose

Context Compaction Memory prevents oversized or high-volume tool output from
entering model context directly. It gives future agents a deterministic way to
preserve full tool output for replay and audit while showing the model only a
bounded, hash-linked envelope unless a bounded retrieval is explicitly requested
and permitted.

The core invariant is:

```text
No model receives unbounded raw tool output.
```

## Threat Model

The layer is designed against these failure modes:

- Tool output is large enough to crowd out instructions, evidence boundaries, or
  safety context.
- Tool output contains raw prompts, tool arguments, payload bodies, messages,
  notes, model reasoning, credentials, host-specific data, or customer-sensitive
  records that should not be copied wholesale into model context.
- A model summary becomes the only retained version of a tool result, causing
  replay to depend on lossy or non-deterministic compression.
- Later retrieval loses provenance for which byte ranges, line ranges, or record
  ranges were visible to the model.
- A future integration treats SIEM, EDR, OCSF, or other vendor output as a
  canonical schema dependency instead of an export/import mapping.

## Architecture Rule

Oversized or high-volume tool output must be:

- stored losslessly in `investigation_memory`;
- represented to the model only through a deterministic bounded envelope;
- referenced by `memory_ref_id`;
- retrievable only through bounded, audited, capability-scoped retrieval;
- recorded in proof/replay artifacts with hashes, byte ranges, retrieval refs,
  and model-visible envelope metadata; and
- never canonically summarized by an LLM.

## Normal Flow

For small, safe, already-bounded tool output:

1. The tool runner records the tool call metadata, output hash, output size, and
   source capability reference.
2. The bounded output can be passed to the model if it satisfies the active
   model-context policy.
3. Proof/replay artifacts record the model-visible output boundary and hash.
4. Replay verifies the recorded hashes and boundaries without calling the live
   tool.

This normal flow is still bounded. It is not permission to place arbitrary raw
tool output in context.

## Oversized-Output Flow

For oversized, high-volume, or policy-sensitive output:

1. The full output is written losslessly to `investigation_memory`.
2. The memory object receives a deterministic `memory_ref_id`.
3. The system computes the full content hash and records byte, line, or record
   indexing metadata where available.
4. A deterministic compacted envelope is generated from policy-defined head and
   tail windows plus metadata about omitted ranges.
5. The model receives only the compacted envelope and `memory_ref_id`.
6. Any later access requires an explicit retrieval request with bounded ranges,
   capability scope, purpose, and audit record.
7. Retrieval results record the exact returned ranges and content hashes.

The compacted envelope is not a semantic summary. It is a deterministic index
view of the preserved output.

## Investigation Memory Role

`investigation_memory` is the future lossless backing store for high-volume tool
output, large artifacts, and range-addressable evidence. It is not implemented
in this PR.

Responsibilities assigned to future implementation:

- Store the exact original bytes or canonical record stream.
- Preserve content hash, size, and source tool-call linkage.
- Support deterministic byte, line, and record ranges.
- Enforce capability-scoped retrieval.
- Emit retrieval audit records for proof/replay.
- Avoid host-specific paths and wall-clock-generated replay values.

## Deterministic Head/Tail Envelope

The model-visible compacted envelope must be deterministic and bounded. It should
include:

- `memory_ref_id`;
- full `content_hash`;
- full `content_size_bytes`;
- envelope policy version;
- included head byte range;
- included tail byte range;
- omitted byte ranges;
- optional line or record range metadata when available;
- envelope hash; and
- source tool-call and capability refs.

The envelope may include bounded head/tail content only when policy permits it.
If content is included, its byte ranges must be explicit and hash-linked. If
content is not included, the envelope still exposes enough metadata for a model
to request a bounded retrieval.

## `memory_ref_id` Semantics

`memory_ref_id` identifies one immutable memory object. The proposed format is:

```text
mem:v1:<investigation_id>:<tool_call_id>:sha256:<content_hash>
```

Where:

- `investigation_id` is the stable investigation or trace identifier.
- `tool_call_id` is the deterministic source tool-call or step identifier.
- `content_hash` is the lowercase SHA-256 hash of the full lossless content.

A `memory_ref_id` must not be reused for changed content. If content changes, the
hash and memory ref change.

## Retrieval Constraints

Retrieval must be bounded, audited, and capability-scoped:

- The request must name `memory_ref_id`.
- The request must name the requester capability or trace record.
- The request must include purpose.
- The request must specify byte ranges, line ranges, or record ranges.
- The request must declare a maximum returned byte count.
- Byte ranges use `[start, end)` bounds and require `end > start`.
- Line ranges use inclusive line bounds and require `end_line >= start_line`.
- Record ranges select exactly one `record_id` or `record_index`.
- The result must record returned ranges, result status, content hash, and audit
  refs.
- The model must receive only the approved bounded result, never the whole
  memory object by default.

Denied, partial, invalid-range, and unavailable results must be explicit.
Failure results must not carry model-visible content. Fulfilled, partial, and
other model-visible results must include at least one returned range, a positive
returned byte count, and a non-null bounded excerpt. Portable JSON Schema
validates the range shapes and result/status consistency; implementations and
validation harnesses must additionally enforce sibling ordering rules such as
`end > start` and `end_line >= start_line`.

## Proof/Replay Implications

Future proof packages and replay artifacts should record:

- `memory_ref_id`;
- full content hash;
- compacted envelope hash;
- model-visible byte, line, or record boundaries;
- retrieval request refs;
- retrieval result refs;
- replay-visible retrieval transcript metadata;
- whether the model saw only the head/tail envelope or retrieved bounded ranges;
- source tool-call refs and capability refs; and
- deterministic unavailable reasons when memory content is absent from an
  exported package.

Replay must be able to prove which ranges were visible to the model without
calling live tools or live memory services.

## Why LLM Summarization Is Not Canonical Compaction

LLM summarization is not canonical compaction because it is lossy,
non-deterministic across model changes, and can omit or transform evidence. It
may be useful as a non-authoritative analyst aid in a future product, but the
canonical compacted representation is the deterministic envelope plus bounded
retrieval transcript.

If an LLM-generated summary is ever recorded, it must be labeled as derived
interpretation and backed by memory refs and retrieval ranges. It must not
replace the lossless memory object or deterministic envelope.

## Boundaries And Non-Goals

This PR does not add:

- runtime memory storage;
- memory retrieval runtime;
- AlertForge output contract or ingest;
- live EDR, SIEM, LLM, DB, Vault, control-plane, or network integrations;
- benchmark harnesses;
- customer-readiness or outreach material;
- signing, anchoring, SLSA, in-toto, or manifest/provenance implementation;
- legal admissibility or compliance certification claims;
- Proof Package V1/V2 verifier behavior changes; or
- V3 adapter behavior changes.

INV-027 applies: these contracts are Zovark canonical contracts and do not make
vendor/proprietary schemas canonical dependencies. Future OCSF, SIEM, or EDR
formats remain mapping/export surfaces only.

INV-028 applies: no current applied/root
`product/features/feature-registry.yaml` file is present in this repo snapshot.
This PR adds architecture/contracts only and does not create an active runtime
feature ID or implementation status. Future product components, standalone
testbed features, AlertForge ingest paths, benchmark harnesses, services,
feature flags, or customer-facing workflows must add or update feature lifecycle
records before implementation claims are made.
