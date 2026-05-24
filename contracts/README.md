# Contracts

Status: contract directory guidance. This README does not make every contract
runtime-enforced.

## Contract Role

Contracts in this directory are Zovark-owned canonical contracts. They define
Zovark architecture surfaces and must remain independent of vendor/proprietary
schemas as canonical dependencies.

Vendor schemas, including future SIEM, EDR, OCSF, or product-specific formats,
are mapping/export surfaces only unless a future INV-027-compatible governance
decision says otherwise.

## Current Contracts

Context Compaction Memory contracts currently have architecture-contract status:

- `context-compaction-envelope-v1.schema.json`
- `memory-retrieval-request-v1.schema.json`
- `memory-retrieval-result-v1.schema.json`

They describe future memory/envelope/retrieval behavior. They do not implement
runtime memory storage, retrieval services, adapter behavior, or verifier
behavior.

## Validation Requirements

Every contract must have valid and invalid examples before it can be treated as
runtime-enforced.

JSON Schema contracts must pass:

- JSON syntax validation;
- JSON Schema metaschema validation;
- practical valid examples; and
- practical invalid examples.

Runtime-enforced status requires:

- implementation code;
- tests;
- valid/invalid fixtures or checks;
- documented failure behavior; and
- review evidence for the implemented enforcement.

## JSON Schema Limitations

JSON Schema cannot portably express all semantic constraints. When a contract
needs semantic helper validation, the limitation must be documented.

Examples include:

- byte range ordering using `[start, end)` with `end > start`;
- line range ordering using inclusive lines with `end_line >= start_line`;
- cross-field consistency between model visibility, returned ranges, returned
  byte counts, and model-visible excerpts; and
- failure states that must carry no model-visible content.

Do not claim runtime enforcement from JSON Schema prose alone.
