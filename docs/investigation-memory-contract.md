# Investigation Memory Contract

Status: architecture/contracts only. This document defines the future
`investigation_memory` object and retrieval contract. It does not implement
storage, retrieval, proof-package emission, Replay verification behavior,
AlertForge integration, live connectors, benchmarks, signing, anchoring, legal
evidence packaging, or customer-facing material.

## Purpose

`investigation_memory` stores lossless, range-addressable tool output and
artifact content that is too large, too high-volume, or too sensitive to place in
model context directly. The model sees deterministic bounded envelopes and, when
permitted, bounded retrieval results.

## Memory Object Identity

Each memory object is immutable and content-addressed.

Required identity fields:

| Field | Meaning |
| --- | --- |
| `memory_ref_id` | Stable identifier for this memory object. |
| `investigation_id` | Stable investigation or trace identifier. |
| `source_tool_call_ref` | Tool-call, step, or trace record that produced the content. |
| `source_capability_ref` | Capability identity that produced or captured the content, when available. |
| `content_hash` | SHA-256 hash of the full lossless content. |
| `content_size_bytes` | Byte length of the full lossless content. |
| `content_encoding` | Encoding or record format used for range addressing. |

Proposed `memory_ref_id` format:

```text
mem:v1:<investigation_id>:<tool_call_id>:sha256:<content_hash>
```

The `memory_ref_id` is not an authorization token. Retrieval still requires
capability-scoped authorization and audit.

## Content Hash Requirements

The full content hash must be computed over the exact lossless stored content.
The compacted envelope hash must be computed over the canonical serialized
envelope after excluding any mutable audit transport fields.

Hash requirements:

- Use lowercase SHA-256 hex.
- Hash full content before compaction.
- Hash each model-visible compacted envelope.
- Hash each bounded retrieval result over the exact returned bytes or canonical
  record subset.
- Record hash algorithm names explicitly.

If future storage encrypts content, the content hash must still refer to the
canonical plaintext or canonical record stream used for replay, not to a
storage-layer ciphertext artifact unless that distinction is explicitly recorded.

## Range Semantics

Memory retrieval can address content by byte, line, or record ranges.

Byte ranges:

- Use zero-based inclusive `start` and exclusive `end`.
- `end` must be greater than `start`.
- The range `[0, content_size_bytes)` represents the full object and must not be
  returned to a model unless an explicit policy permits full bounded output.

Line ranges:

- Use one-based inclusive `start_line` and inclusive `end_line`.
- `end_line` must be greater than or equal to `start_line`.
- Line numbering is derived from the canonical decoded content.
- Line range metadata should record the byte range when deterministic mapping is
  available.

Record ranges:

- Use exactly one deterministic record identifier or zero-based record index.
- Record order must be stable under replay.
- Record hashes should be recorded when individual record hashing is available.

The JSON Schema contracts require the correct field set and reject unknown
properties for each range type. Portable JSON Schema draft 2020-12 does not
compare sibling values such as `end > start` or `end_line >= start_line`
without nonstandard extensions, so implementations and validation harnesses must
enforce those ordering rules as semantic checks in addition to schema shape
validation.

## Source Tool-Call Linkage

Every memory object must link back to the source that produced it:

- source tool-call or step ref;
- source capability ref when available;
- input hash or input ref when captured;
- output hash;
- execution status; and
- trace or investigation record refs when available.

This linkage lets future Proof Package V2 and Replay records distinguish:

- output the model saw as a compacted envelope;
- output retrieved later through bounded ranges; and
- output preserved losslessly but never shown to the model.

## Retention Assumptions

This contract does not set a product retention period. Future retention policy
must specify:

- whether memory content is exported inside proof packages or kept in a local
  evidence store;
- whether exported packages include only envelopes and hashes;
- how unavailable retained content is represented during replay;
- when deletion, legal hold, or tenant offboarding policy applies; and
- how memory refs are invalidated or tombstoned without reusing identifiers.

Do not claim forensic completeness or legal admissibility from this retention
contract.

## Retrieval Audit Record Requirements

Every retrieval attempt must produce an audit record, including denied attempts.

Required retrieval audit metadata:

| Field | Meaning |
| --- | --- |
| `retrieval_request_id` | Deterministic request identifier. |
| `memory_ref_id` | Memory object requested. |
| `requester_capability_ref` | Capability or trace record making the request. |
| `purpose` | Bounded purpose for retrieval. |
| `requested_ranges` | Byte, line, or record ranges requested. |
| `max_bytes` | Maximum bytes allowed in the result. |
| `decision` | `approved`, `partial`, `denied`, `not_found`, or `range_invalid`. |
| `returned_ranges` | Ranges actually returned. |
| `result_hash` | Hash of returned bounded content or canonical empty result. |
| `model_visible` | Whether the bounded result was placed into model context. |

Audit records must be deterministic and replay-visible. They must not depend on
wall-clock values generated during replay.

Retrieval result consistency requirements:

- `fulfilled` and `partial` results must be model-visible, return at least one
  bounded range, return a positive byte count, and carry a non-null bounded
  model-visible excerpt.
- Any result with `model_visible: true` must return at least one bounded range,
  return a positive byte count, and carry a non-null bounded model-visible
  excerpt.
- `denied`, `not_found`, `range_invalid`, and `unavailable` results must not
  carry model-visible content. They must use `model_visible: false`, empty
  `returned_ranges`, `returned_byte_count: 0`, and a non-null unavailable reason
  appropriate to the failure status.

## Capability-Scoped Access Rules

Future retrieval must be scoped by capability:

- A capability can retrieve only memory objects within its investigation scope.
- A capability can retrieve only ranges permitted by policy.
- A retrieval can return less than requested.
- A retrieval can be denied without exposing content.
- A retrieval result must not include raw tool arguments, raw prompts, raw tool
  outputs, payload bodies, messages, notes, or hidden reasoning beyond the
  explicitly approved bounded range.

Policy decisions must be auditable. A model must not request or receive
unbounded memory content by convention or default.

## Deterministic Replay Requirements

Replay must be able to reconstruct and verify:

- memory object identity;
- full content hash when content is present;
- compacted envelope hash;
- source tool-call linkage;
- model-visible ranges;
- retrieval requests;
- retrieval results;
- denied or partial retrievals; and
- unavailable content reasons.

Replay must not call live memory storage, live tools, live EDR/SIEM systems, live
LLMs, databases, Vault, control-plane services, or network services.

## Contract Schema Files

Root-level contract schemas are introduced under `contracts/` because the
current repo snapshot has no applied/root schema directory. Recovered patch-tree
schemas exist under historical `zovark-v3.2.4.6...` material, but this PR does
not make that patch-tree path a canonical current schema location.

Current contract files:

- `contracts/context-compaction-envelope-v1.schema.json`
- `contracts/memory-retrieval-request-v1.schema.json`
- `contracts/memory-retrieval-result-v1.schema.json`

These schemas define the architecture contract surface only. They are not wired
into runtime storage, adapter output, or verifier behavior.

## Non-Goals

This contract does not add:

- runtime storage implementation;
- retrieval service implementation;
- product feature lifecycle activation;
- AlertForge contract or ingest;
- benchmark harness;
- customer-readiness material;
- signing, anchoring, SLSA, in-toto, or external provenance;
- legal admissibility or compliance certification claims; or
- changes to Proof Package V1/V2 generation or verification.
