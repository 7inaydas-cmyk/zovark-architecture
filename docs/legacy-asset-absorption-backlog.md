# Legacy Asset Absorption Backlog

Status: backlog and salvage classification only. This document does not import
legacy code, implement RamaLama, add runtime behavior, create benchmarks, or make
customer-readiness claims.

## Zovark_swami Local-Inference Work

The recovered `Zovark_swami` local-inference work is reclassified from deferred
future capability to salvage source for RamaLama integration under the ADR-0009
amendment.

Candidate salvage items:

- `llama-server` local-inference setup
- Gemma 4 E4B local model experiments
- `models/zovark-dpo-adapter`
- QLoRA work on `Qwen2.5-14B-Instruct`

## Portability Constraints

The existing DPO dataset assumes the older code-generation interaction shape.
It is not directly portable to the current bounded-envelope model-context
semantics. Any future adapter or retraining work must preserve the Context
Compaction Memory invariant:

```text
No model receives unbounded raw tool output.
```

Retraining under bounded-envelope semantics is required before the adapter is
portable.

## Mapping To ADR-0009

The two-model architecture from `Zovark_swami` maps to the ADR-0009 split:

- FAST role: low-latency tool selection, routing, and parameter filling.
- CODE role: deeper investigation generation or synthesis work where approved.

Under the v3.2.4.4 amendment, the local-SLM runtime named for this topology is
RamaLama. Cloud/local/hybrid inference remain planned target topology choices,
pending runtime implementation, operator controls, and validation. They are not
currently tenant-selectable runtime capabilities. Replay/evidence-integrity
positioning does not depend on local inference being available.

## Not Yet Accepted

This backlog does not make the recovered local-inference artifacts canonical
runtime code. Before implementation, a future PR must reconcile:

- model provenance and licensing;
- prompt/version/hash records;
- bounded envelope semantics;
- evidence and replay records;
- benchmark provenance under INV-022; and
- tenant topology configuration under ADR-0038 and ADR-0009.