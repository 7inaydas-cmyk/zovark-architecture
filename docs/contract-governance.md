# Contract Governance

Status: governance policy for architecture contracts and schemas. This document
does not implement runtime enforcement, change adapter behavior, change verifier
behavior, or add integration scope.

## Contract Status Values

Use these status values for Zovark-owned contracts:

| Status | Meaning |
| --- | --- |
| `draft-architecture-contract` | Architecture contract exists, but runtime enforcement is not implemented. |
| `runtime-enforced` | Runtime enforcement exists and is covered by tests plus valid/invalid fixtures or checks. |
| `deprecated` | Contract remains for historical reference but should not be used for new work. |
| `superseded` | Contract has been replaced by a named newer contract. |

Do not claim `runtime-enforced` without implementation code, tests, and
valid/invalid examples.

## Schema Validation Requirements

Every JSON Schema contract must pass:

- JSON syntax validation;
- JSON Schema metaschema validation;
- practical valid examples; and
- practical invalid examples.

Schema PRs must report the exact accepted and rejected examples used during
validation.

## Semantic Validation Requirements

JSON Schema draft 2020-12 cannot portably express every cross-field or sibling
ordering rule. Those limitations must be documented in the schema or nearby
contract docs, and practical helper validation must cover them.

Required semantic checks include:

- byte range ordering using `[start, end)` with `end > start`;
- line range ordering with `end_line >= start_line`;
- record range selector exclusivity where a shape requires exactly one selector;
- cross-field consistency such as model-visible content requiring explicit
  returned ranges and positive byte counts; and
- failure states that must not carry model-visible content.

If a semantic constraint is not covered by pure JSON Schema, do not imply that
JSON Schema alone enforces it.

## Model-Visible Data Contracts

Model-visible data contracts must bind visibility to exact ranges and byte
counts. A model-visible result must not be represented by generic prose,
unbounded fields, or package-wide references.

For Context Compaction Memory contracts, model-visible results must record:

- memory reference;
- returned ranges;
- returned byte count;
- result hash;
- whether the result was model-visible; and
- bounded excerpt or explicit failure state.

## Runtime Enforcement Claims

Architecture contracts may describe future requirements. They must not claim
runtime enforcement until:

- implementation code exists;
- tests cover enforcement;
- valid and invalid fixtures/checks exist;
- failure behavior is explicit; and
- review evidence confirms the implemented behavior.

## Vendor Schema Boundary

ADR-0036 applies. Vendor schemas remain mapping/export surfaces unless an
ADR-0036-compatible governance decision explicitly approves otherwise.

Zovark-owned contracts must not make OCSF, SIEM, EDR, or other vendor schemas
canonical dependencies for replay, audit, storage, verdict, or customer evidence.
